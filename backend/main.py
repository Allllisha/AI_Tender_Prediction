from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
import uvicorn
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# データベース関連
from database import engine
import database
# import models as db_models  # コメントアウト - modelsファイルは存在しない

# 既存のPydanticモデル
from old_models import (
    TenderSearch, PredictionRequest, BulkPredictionRequest,
    PredictionResponse, TenderInfo
)
from data_loader import DataLoader
from predictor import BidPredictor

# ルーター
from routers import auth_router, csv_upload_router, company_router

# テーブル作成はスキップ（既にPostgreSQLで1_init.sqlで作成済み）
# db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="建築入札インテリジェンス・システム",
    description="AI駆動型入札分析システム",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

data_loader = DataLoader()
predictor = BidPredictor(data_loader)

# ルーターを登録
app.include_router(auth_router.router)
app.include_router(csv_upload_router.router)
app.include_router(company_router.router)

# OAuth2-compatible login endpoint for form data
@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    """OAuth2 compatible login endpoint that accepts form data"""
    from auth import authenticate_company, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
    from datetime import timedelta
    
    # Authenticate using email/username as email
    company = authenticate_company(db, form_data.username, form_data.password)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"company_id": company.id, "email": company.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "company_id": company.id,
        "company_name": company.company_name,
        "email": company.email
    }

@app.get("/")
def read_root():
    return {
        "message": "建築入札インテリジェンス・システム API",
        "version": "1.0.0",
        "endpoints": [
            "/auth/login - ログイン",
            "/auth/me - 現在の企業情報",
            "/csv/upload-awards - 落札実績CSVアップロード",
            "/csv/download-template - CSVテンプレート",
            "/company/strengths - 会社の強み分析",
            "/tenders/search - 案件検索",
            "/tenders/{tender_id} - 案件詳細",
            "/predict - 勝率予測",
            "/predict-bulk - 一括予測"
        ]
    }

@app.get("/tenders/search", response_model=List[TenderInfo])
def search_tenders(
    prefecture: Optional[str] = None,
    municipality: Optional[str] = None,
    use_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    bid_method: Optional[str] = None
):
    filters = {}
    if prefecture:
        filters['prefecture'] = prefecture
    if municipality:
        filters['municipality'] = municipality
    if use_type:
        filters['use_type'] = use_type
    if min_price:
        filters['min_price'] = min_price
    if max_price:
        filters['max_price'] = max_price
    if bid_method:
        filters['bid_method'] = bid_method
        
    results = data_loader.search_tenders(**filters)
    return results

@app.get("/tenders/{tender_id}", response_model=TenderInfo)
def get_tender(tender_id: str):
    tender = data_loader.get_tender_by_id(tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender

@app.post("/predict", response_model=PredictionResponse)
def predict_single(request: PredictionRequest):
    try:
        result = predictor.predict_single(
            request.tender_id,
            request.bid_amount,
            request.company_name
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-bulk", response_model=List[PredictionResponse])
def predict_bulk(request: BulkPredictionRequest):
    try:
        search_params = {}
        if request.prefecture:
            search_params['prefecture'] = request.prefecture
        if request.municipality:
            search_params['municipality'] = request.municipality
        if request.use_type:
            search_params['use_type'] = request.use_type
            
        results = predictor.predict_bulk(
            search_params,
            request.bid_amount,
            request.company_name,
            use_ratio=request.use_ratio,
            min_price=request.min_price,
            max_price=request.max_price
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/company/strengths")
def get_company_strengths(company_name: Optional[str] = None):
    try:
        if not company_name:
            company_name = "星田建設株式会社"
        strengths = data_loader.get_company_strengths(company_name)
        return strengths
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/filters/options")
def get_filter_options():
    prefectures = set()
    municipalities = set()
    use_types = set()
    bid_methods = set()
    
    # 都道府県ごとの市区町村を格納
    prefecture_municipalities = {}
    
    for tender in data_loader.tender_data:
        prefecture = tender['prefecture']
        municipality = tender['municipality']
        
        prefectures.add(prefecture)
        municipalities.add(municipality)
        use_types.add(tender['use_type'])
        bid_methods.add(tender['bid_method'])
        
        # 都道府県ごとに市区町村を分類
        if prefecture not in prefecture_municipalities:
            prefecture_municipalities[prefecture] = set()
        prefecture_municipalities[prefecture].add(municipality)
    
    # 都道府県ごとの市区町村リストをソート
    for prefecture in prefecture_municipalities:
        prefecture_municipalities[prefecture] = sorted(list(prefecture_municipalities[prefecture]))
    
    return {
        "prefectures": sorted(list(prefectures)),
        "municipalities": sorted(list(municipalities)),
        "use_types": sorted(list(use_types)),
        "bid_methods": sorted(list(bid_methods)),
        "prefecture_municipalities": prefecture_municipalities
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)