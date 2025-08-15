"""
会社分析関連のAPIエンドポイント
"""
from typing import Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from database import get_db
from auth import get_current_company
import models

router = APIRouter(prefix="/company", tags=["会社分析"])

class CompanyStrengthsResponse(BaseModel):
    """会社の強み分析レスポンス"""
    company_name: str
    total_awards: int
    total_amount: int
    avg_amount: float
    avg_win_rate: float
    strongest_prefecture: str = None
    prefectures: Dict[str, int]
    strongest_use_type: str = None
    use_types: Dict[str, int]
    bid_methods: Dict[str, int]
    avg_tech_score: float = None

@router.get("/strengths", response_model=CompanyStrengthsResponse)
async def get_company_strengths(
    db: Session = Depends(get_db),
    current_company: models.Company = Depends(get_current_company)
):
    """
    会社の強み分析データを取得
    
    過去の落札実績から以下を分析:
    - 総落札件数・金額
    - 地域別実績
    - 用途別実績
    - 入札方式別実績
    - 平均技術点
    """
    
    # 基本統計を取得
    stats = db.query(
        func.count(models.CompanyAward.id).label("total_awards"),
        func.sum(models.CompanyAward.award_amount_jpy).label("total_amount"),
        func.avg(models.CompanyAward.award_amount_jpy).label("avg_amount"),
        func.avg(models.CompanyAward.win_rate).label("avg_win_rate")
    ).filter(
        models.CompanyAward.company_id == current_company.id
    ).first()
    
    # データが存在しない場合のデフォルト値
    if not stats.total_awards:
        return CompanyStrengthsResponse(
            company_name=current_company.company_name,
            total_awards=0,
            total_amount=0,
            avg_amount=0,
            avg_win_rate=0,
            prefectures={},
            use_types={},
            bid_methods={}
        )
    
    # 都道府県別実績
    prefecture_stats = db.query(
        models.CompanyAward.prefecture,
        func.count(models.CompanyAward.id).label("count")
    ).filter(
        models.CompanyAward.company_id == current_company.id
    ).group_by(models.CompanyAward.prefecture).all()
    
    prefectures = {p.prefecture: p.count for p in prefecture_stats if p.prefecture}
    strongest_prefecture = max(prefectures, key=prefectures.get) if prefectures else None
    
    # 用途別実績
    use_type_stats = db.query(
        models.CompanyAward.use_type,
        func.count(models.CompanyAward.id).label("count")
    ).filter(
        models.CompanyAward.company_id == current_company.id
    ).group_by(models.CompanyAward.use_type).all()
    
    use_types = {u.use_type: u.count for u in use_type_stats if u.use_type}
    strongest_use_type = max(use_types, key=use_types.get) if use_types else None
    
    # 入札方式別実績
    method_stats = db.query(
        models.CompanyAward.method,
        func.count(models.CompanyAward.id).label("count")
    ).filter(
        models.CompanyAward.company_id == current_company.id
    ).group_by(models.CompanyAward.method).all()
    
    bid_methods = {m.method: m.count for m in method_stats if m.method}
    
    # 平均技術点（総合評価方式のみ）
    avg_tech_score = db.query(
        func.avg(models.CompanyAward.technical_score)
    ).filter(
        models.CompanyAward.company_id == current_company.id,
        models.CompanyAward.technical_score.isnot(None)
    ).scalar()
    
    return CompanyStrengthsResponse(
        company_name=current_company.company_name,
        total_awards=stats.total_awards or 0,
        total_amount=int(stats.total_amount or 0),
        avg_amount=float(stats.avg_amount or 0),
        avg_win_rate=float(stats.avg_win_rate or 0),
        strongest_prefecture=strongest_prefecture,
        prefectures=prefectures,
        strongest_use_type=strongest_use_type,
        use_types=use_types,
        bid_methods=bid_methods,
        avg_tech_score=float(avg_tech_score) if avg_tech_score else None
    )

@router.get("/performance-by-region")
async def get_performance_by_region(
    db: Session = Depends(get_db),
    current_company: models.Company = Depends(get_current_company)
):
    """
    地域別のパフォーマンス詳細を取得
    """
    results = db.query(
        models.CompanyAward.prefecture,
        models.CompanyAward.municipality,
        func.count(models.CompanyAward.id).label("count"),
        func.avg(models.CompanyAward.win_rate).label("avg_win_rate"),
        func.sum(models.CompanyAward.award_amount_jpy).label("total_amount")
    ).filter(
        models.CompanyAward.company_id == current_company.id
    ).group_by(
        models.CompanyAward.prefecture,
        models.CompanyAward.municipality
    ).order_by(
        func.count(models.CompanyAward.id).desc()
    ).all()
    
    return [
        {
            "prefecture": r.prefecture,
            "municipality": r.municipality,
            "count": r.count,
            "avg_win_rate": float(r.avg_win_rate) if r.avg_win_rate else 0,
            "total_amount": int(r.total_amount) if r.total_amount else 0
        }
        for r in results
    ]

@router.get("/performance-by-type")
async def get_performance_by_type(
    db: Session = Depends(get_db),
    current_company: models.Company = Depends(get_current_company)
):
    """
    用途種別別のパフォーマンス詳細を取得
    """
    results = db.query(
        models.CompanyAward.use_type,
        func.count(models.CompanyAward.id).label("count"),
        func.avg(models.CompanyAward.win_rate).label("avg_win_rate"),
        func.avg(models.CompanyAward.floor_area_m2).label("avg_floor_area"),
        func.sum(models.CompanyAward.award_amount_jpy).label("total_amount")
    ).filter(
        models.CompanyAward.company_id == current_company.id
    ).group_by(
        models.CompanyAward.use_type
    ).order_by(
        func.count(models.CompanyAward.id).desc()
    ).all()
    
    return [
        {
            "use_type": r.use_type,
            "count": r.count,
            "avg_win_rate": float(r.avg_win_rate) if r.avg_win_rate else 0,
            "avg_floor_area": float(r.avg_floor_area) if r.avg_floor_area else 0,
            "total_amount": int(r.total_amount) if r.total_amount else 0
        }
        for r in results
    ]