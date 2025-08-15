"""
CSVアップロード関連のAPIエンドポイント
"""
import io
import csv
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from auth import get_current_company
import models
import pandas as pd

router = APIRouter(prefix="/csv", tags=["CSVアップロード"])

class UploadHistoryResponse(BaseModel):
    """アップロード履歴レスポンス"""
    id: int
    file_name: str
    record_count: int
    upload_status: str
    error_message: str = None
    uploaded_at: datetime
    completed_at: datetime = None

class CompanyAwardResponse(BaseModel):
    """会社落札実績レスポンス"""
    id: int
    tender_id: str
    project_name: str
    publisher: str
    prefecture: str
    municipality: str
    use_type: str
    method: str
    floor_area_m2: float
    award_date: str
    award_amount_jpy: int
    estimated_price_jpy: int
    win_rate: float
    participants_count: int
    technical_score: float = None

@router.post("/upload-awards")
async def upload_company_awards(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_company: models.Company = Depends(get_current_company)
):
    """
    会社の落札実績CSVをアップロード
    
    CSVフォーマット:
    - tender_id: 案件ID
    - project_name: 工事名
    - publisher: 発注者
    - prefecture: 都道府県
    - municipality: 市区町村
    - use_type: 用途種別
    - method: 入札方式
    - floor_area_m2: 延床面積
    - award_date: 落札日 (YYYY-MM-DD)
    - award_amount_jpy: 落札額
    - estimated_price_jpy: 予定価格
    - win_rate: 落札率
    - participants_count: 参加社数
    - technical_score: 技術点（総合評価方式の場合）
    """
    
    # ファイルの検証
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSVファイルのみアップロード可能です"
        )
    
    # アップロード履歴を作成
    upload_history = models.CSVUploadHistory(
        company_id=current_company.id,
        file_name=file.filename,
        upload_status="processing",
        uploaded_at=datetime.utcnow()
    )
    db.add(upload_history)
    db.commit()
    
    try:
        # CSVファイルを読み込む
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # 必須カラムの確認
        required_columns = [
            'tender_id', 'project_name', 'publisher', 'prefecture',
            'municipality', 'use_type', 'method', 'floor_area_m2',
            'award_date', 'award_amount_jpy', 'estimated_price_jpy',
            'win_rate', 'participants_count'
        ]
        
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"必須カラムが不足しています: {', '.join(missing_columns)}")
        
        # 既存のデータを削除（オプション：重複を避けるため）
        existing_tender_ids = df['tender_id'].tolist()
        db.query(models.CompanyAward).filter(
            models.CompanyAward.company_id == current_company.id,
            models.CompanyAward.tender_id.in_(existing_tender_ids)
        ).delete(synchronize_session=False)
        
        # データを登録
        records_added = 0
        for _, row in df.iterrows():
            award = models.CompanyAward(
                company_id=current_company.id,
                tender_id=str(row['tender_id']),
                project_name=str(row['project_name']),
                publisher=str(row['publisher']),
                prefecture=str(row['prefecture']),
                municipality=str(row['municipality']),
                use_type=str(row['use_type']),
                method=str(row['method']),
                floor_area_m2=float(row['floor_area_m2']),
                award_date=pd.to_datetime(row['award_date']).date(),
                award_amount_jpy=int(row['award_amount_jpy']),
                estimated_price_jpy=int(row['estimated_price_jpy']),
                win_rate=float(row['win_rate']),
                participants_count=int(row['participants_count']),
                technical_score=float(row['technical_score']) if pd.notna(row.get('technical_score')) else None
            )
            db.add(award)
            records_added += 1
        
        # コミット
        db.commit()
        
        # アップロード履歴を更新
        upload_history.upload_status = "completed"
        upload_history.record_count = records_added
        upload_history.completed_at = datetime.utcnow()
        db.commit()
        
        return {
            "message": f"{records_added}件のデータを正常にアップロードしました",
            "upload_id": upload_history.id,
            "record_count": records_added
        }
        
    except Exception as e:
        # エラー時の処理
        upload_history.upload_status = "failed"
        upload_history.error_message = str(e)
        upload_history.completed_at = datetime.utcnow()
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSVの処理中にエラーが発生しました: {str(e)}"
        )

@router.get("/upload-history", response_model=List[UploadHistoryResponse])
async def get_upload_history(
    db: Session = Depends(get_db),
    current_company: models.Company = Depends(get_current_company)
):
    """
    CSVアップロード履歴を取得
    """
    history = db.query(models.CSVUploadHistory).filter(
        models.CSVUploadHistory.company_id == current_company.id
    ).order_by(models.CSVUploadHistory.uploaded_at.desc()).all()
    
    return [
        UploadHistoryResponse(
            id=h.id,
            file_name=h.file_name,
            record_count=h.record_count or 0,
            upload_status=h.upload_status,
            error_message=h.error_message,
            uploaded_at=h.uploaded_at,
            completed_at=h.completed_at
        )
        for h in history
    ]

@router.get("/company-awards", response_model=List[CompanyAwardResponse])
async def get_company_awards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_company: models.Company = Depends(get_current_company)
):
    """
    会社の落札実績を取得
    """
    awards = db.query(models.CompanyAward).filter(
        models.CompanyAward.company_id == current_company.id
    ).order_by(models.CompanyAward.award_date.desc()).offset(skip).limit(limit).all()
    
    return [
        CompanyAwardResponse(
            id=a.id,
            tender_id=a.tender_id,
            project_name=a.project_name,
            publisher=a.publisher,
            prefecture=a.prefecture,
            municipality=a.municipality,
            use_type=a.use_type,
            method=a.method,
            floor_area_m2=float(a.floor_area_m2),
            award_date=a.award_date.isoformat(),
            award_amount_jpy=a.award_amount_jpy,
            estimated_price_jpy=a.estimated_price_jpy,
            win_rate=float(a.win_rate),
            participants_count=a.participants_count,
            technical_score=float(a.technical_score) if a.technical_score else None
        )
        for a in awards
    ]

@router.get("/download-template")
async def download_csv_template():
    """
    CSVテンプレートをダウンロード
    """
    template_data = {
        "tender_id": ["SAMPLE-001", "SAMPLE-002"],
        "project_name": ["〇〇小学校改築工事", "△△庁舎耐震補強工事"],
        "publisher": ["東京都", "神奈川県"],
        "prefecture": ["東京都", "神奈川県"],
        "municipality": ["新宿区", "横浜市"],
        "use_type": ["学校", "庁舎"],
        "method": ["一般競争入札", "総合評価方式"],
        "floor_area_m2": [3500.5, 4200.0],
        "award_date": ["2024-01-15", "2024-02-20"],
        "award_amount_jpy": [450000000, 680000000],
        "estimated_price_jpy": [500000000, 750000000],
        "win_rate": [90.0, 90.7],
        "participants_count": [5, 8],
        "technical_score": [85.5, 92.0]
    }
    
    df = pd.DataFrame(template_data)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    from fastapi.responses import StreamingResponse
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=company_awards_template.csv"
        }
    )