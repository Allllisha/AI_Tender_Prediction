"""
旧Pydanticモデル定義（既存コードとの互換性維持用）
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class TenderSearch(BaseModel):
    prefecture: Optional[str] = None
    municipality: Optional[str] = None
    use_type: Optional[str] = None
    min_floor_area: Optional[float] = None
    max_floor_area: Optional[float] = None
    bid_date_start: Optional[str] = None
    bid_date_end: Optional[str] = None

class TenderInfo(BaseModel):
    tender_id: str
    title: str  # Changed from project_name to match data
    publisher: str
    prefecture: str
    municipality: str
    use_type: str
    floor_area_m2: float
    bid_date: str
    estimated_price: Optional[int] = None
    minimum_price: Optional[int] = None  # Changed from min_price
    bid_method: str = "一般競争入札"  # Changed from method
    jv_allowed: bool = False

class PredictionRequest(BaseModel):
    tender_id: str
    bid_amount: int
    company_name: str = "星田建設株式会社"

class BulkPredictionRequest(BaseModel):
    prefecture: Optional[str] = None
    municipality: Optional[str] = None
    use_type: Optional[str] = None
    bid_amount: int
    company_name: str = "星田建設株式会社"
    use_ratio: bool = True
    min_price: Optional[int] = None
    max_price: Optional[int] = None

class SimilarCase(BaseModel):
    contractor: str
    contract_amount: int
    contract_amount_display: str
    prefecture: str
    use_type: str
    bid_method: str
    award_date: str
    participants_count: Optional[int] = None

class PredictionResponse(BaseModel):
    tender_id: str
    title: str  # Changed from project_name to match data
    rank: str
    win_probability: float
    confidence: str
    basis: Dict[str, Any]
    judgment_reason: str  # 判断理由を追加
    risk_notes: List[str]
    similar_cases: List[Dict[str, Any]]  # 類似案件の詳細を追加
    recommendation: str
    top_factors: List[Dict[str, Any]]