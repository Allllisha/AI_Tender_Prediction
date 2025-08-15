"""
データベースモデル定義
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, DECIMAL, Text, BigInteger, Index
from sqlalchemy.orm import relationship
from database import Base

class Company(Base):
    """建設会社マスタ"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    company_code = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    awards = relationship("CompanyAward", back_populates="company", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="company", cascade="all, delete-orphan")
    uploads = relationship("CSVUploadHistory", back_populates="company", cascade="all, delete-orphan")


class CompanyAward(Base):
    """会社別落札実績"""
    __tablename__ = "company_awards"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    tender_id = Column(String(100))
    project_name = Column(String(500))
    publisher = Column(String(200))
    prefecture = Column(String(50), index=True)
    municipality = Column(String(100))
    address_text = Column(Text)
    use_type = Column(String(100))
    method = Column(String(100))
    floor_area_m2 = Column(DECIMAL(10, 2))
    award_date = Column(Date, index=True)
    award_amount_jpy = Column(BigInteger)
    estimated_price_jpy = Column(BigInteger)
    win_rate = Column(DECIMAL(5, 2))  # 落札率
    participants_count = Column(Integer)
    technical_score = Column(DECIMAL(5, 2))  # 総合評価方式の技術点
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # リレーション
    company = relationship("Company", back_populates="awards")
    
    # 複合インデックス
    __table_args__ = (
        Index('idx_company_tender', 'company_id', 'tender_id', unique=True),
    )


class UserSession(Base):
    """ユーザーセッション管理"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーション
    company = relationship("Company", back_populates="sessions")


class CSVUploadHistory(Base):
    """CSVアップロード履歴"""
    __tablename__ = "csv_upload_history"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255))
    record_count = Column(Integer)
    upload_status = Column(String(50))  # 'processing', 'completed', 'failed'
    error_message = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # リレーション
    company = relationship("Company", back_populates="uploads")