from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
import uvicorn
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
# import pandas as pd  # Not used

# 環境変数の読み込み（ローカル開発時のみ）
# Docker/App Serviceでは環境変数が直接設定されるため不要
if os.path.exists('.env'):
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

# デモユーザーの自動作成は本番環境では無効化
# def create_demo_user_on_startup():
#     """アプリケーション起動時にデモユーザーを作成"""
#     # 本番環境では手動でユーザーを作成してください
#     pass

app = FastAPI(
    title="建築入札インテリジェンス・システム",
    description="AI駆動型入札分析システム",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # すべてのオリジンを許可
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

@app.get("/filters/options")
def get_filter_options():
    """フィルタオプションを取得"""
    try:
        return data_loader.get_filter_options()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tenders/search")
def search_tenders(
    prefecture: Optional[str] = None,
    municipality: Optional[str] = None,
    use_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    bid_method: Optional[str] = None
):
    try:
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
            
        results = data_loader.search_tenders(filters)
        
        # 既に辞書のリストが返ってくるので、そのまま返す
        if not results:
            return []
        
        # 日付フォーマットの処理
        for result in results:
            # 日付型を文字列に変換
            if result.get('bid_date'):
                result['bid_date'] = result['bid_date'].strftime('%Y-%m-%d') if result['bid_date'] else ''
            if result.get('notice_date'):
                result['notice_date'] = result['notice_date'].strftime('%Y-%m-%d') if result['notice_date'] else ''
            
            # Noneをデフォルト値に変換
            result['floor_area_m2'] = result.get('floor_area_m2') or 0
            result['estimated_price'] = result.get('estimated_price') or 0
            result['minimum_price'] = result.get('minimum_price') or 0
            result['jv_allowed'] = result.get('jv_allowed') or False
            
            # 文字列のNoneを空文字に
            for key in ['tender_id', 'title', 'publisher', 'prefecture', 'municipality', 
                       'address_text', 'use_type', 'bid_method', 'origin_url']:
                if key in result and result[key] is None:
                    result[key] = ''
        
        return results
    except Exception as e:
        print(f"Error in search_tenders: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tenders/{tender_id}", response_model=TenderInfo)
def get_tender(tender_id: str):
    tender = data_loader.get_tender_by_id(tender_id)
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")
    return tender

@app.post("/predict", response_model=PredictionResponse)
def predict_single(request: PredictionRequest):
    try:
        print(f"Predict request: tender_id={request.tender_id}, bid_amount={request.bid_amount}, company_name={request.company_name}")
        result = predictor.predict_single(
            request.tender_id,
            request.bid_amount,
            request.company_name
        )
        print(f"Predict result: {result}")
        return result
    except ValueError as e:
        print(f"ValueError in predict: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error in predict: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict-bulk", response_model=List[PredictionResponse])
def predict_bulk(request: BulkPredictionRequest):
    try:
        print(f"Bulk prediction request: {request}")
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
        print(f"Bulk prediction results: {len(results) if results else 0} items")
        return results
    except Exception as e:
        print(f"Error in predict_bulk: {e}")
        import traceback
        traceback.print_exc()
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)