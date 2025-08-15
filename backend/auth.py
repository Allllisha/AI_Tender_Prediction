"""
認証・認可関連のユーティリティ
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
import models

# 環境変数から取得（本番環境では必ず変更すること）
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24時間

# パスワードハッシュ化のコンテキスト
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTPベアラー認証
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """パスワードの検証"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """パスワードのハッシュ化"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """アクセストークンの作成"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """トークンの検証"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_company(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.Company:
    """現在のログイン企業を取得"""
    token = credentials.credentials
    
    # トークンを検証
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効な認証情報です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # トークンから企業IDを取得
    company_id = payload.get("company_id")
    if company_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無効な認証情報です",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # データベースから企業情報を取得
    company = db.query(models.Company).filter(
        models.Company.id == company_id,
        models.Company.is_active == True
    ).first()
    
    if company is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="企業情報が見つかりません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return company

def authenticate_company(db: Session, email: str, password: str) -> Optional[models.Company]:
    """企業の認証"""
    company = db.query(models.Company).filter(
        models.Company.email == email,
        models.Company.is_active == True
    ).first()
    
    if not company:
        return None
    
    if not verify_password(password, company.password_hash):
        return None
    
    return company