"""
認証関連のAPIエンドポイント
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from auth import (
    authenticate_company,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_company
)
import models

router = APIRouter(prefix="/auth", tags=["認証"])

class LoginRequest(BaseModel):
    """ログインリクエスト"""
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    """ログインレスポンス"""
    token: str
    company_id: int
    company_name: str
    email: str

class CompanyInfo(BaseModel):
    """企業情報"""
    company_id: int
    company_code: str
    company_name: str
    email: str
    is_active: bool

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    ログインエンドポイント
    
    メールアドレスとパスワードで認証し、JWTトークンを返す
    """
    # 企業を認証
    company = authenticate_company(db, request.email, request.password)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # アクセストークンを作成
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"company_id": company.id, "email": company.email},
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        token=access_token,
        company_id=company.id,
        company_name=company.company_name,
        email=company.email
    )

@router.get("/me", response_model=CompanyInfo)
async def get_current_company_info(
    current_company: models.Company = Depends(get_current_company)
):
    """
    現在ログイン中の企業情報を取得
    
    認証トークンが必要
    """
    return CompanyInfo(
        company_id=current_company.id,
        company_code=current_company.company_code,
        company_name=current_company.company_name,
        email=current_company.email,
        is_active=current_company.is_active
    )

@router.post("/logout")
async def logout():
    """
    ログアウトエンドポイント
    
    クライアント側でトークンを削除することでログアウトを実現
    """
    return {"message": "ログアウトしました"}