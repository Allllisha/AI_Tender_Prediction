from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    company_code = Column(String(20))
    company_name = Column(String(200), unique=True, index=True)
    email = Column(String(200), unique=True, index=True)
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    company = relationship("Company", backref="users")
    
class CompanyAward(Base):
    __tablename__ = "company_awards"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    tender_id = Column(String(100))
    project_name = Column(String(500))
    publisher = Column(String(200))
    prefecture = Column(String(50))
    municipality = Column(String(100))
    address_text = Column(Text)
    use_type = Column(String(100))
    method = Column(String(100))
    floor_area_m2 = Column(Float)
    award_date = Column(DateTime)
    award_amount_jpy = Column(Integer)
    estimated_price_jpy = Column(Integer)
    win_rate = Column(Float)
    participants_count = Column(Integer)
    technical_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    company = relationship("Company", backref="awards")

class CompanyStrength(Base):
    __tablename__ = "company_strengths"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    prefecture = Column(String)
    use_type = Column(String)
    procurement_method = Column(String)
    win_rate = Column(Float)
    average_bid_amount = Column(Float)
    total_projects = Column(Integer)
    
    company = relationship("Company", backref="strengths")

class UploadHistory(Base):
    __tablename__ = "upload_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    upload_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    records_processed = Column(Integer)
    error_message = Column(Text, nullable=True)
    
    user = relationship("User", backref="uploads")

class CSVUploadHistory(Base):
    __tablename__ = "csv_upload_history"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    file_name = Column(String(500))
    upload_status = Column(String(50))  # 'processing', 'completed', 'failed'
    record_count = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    company = relationship("Company", backref="csv_uploads")