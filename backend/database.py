"""
データベース接続とセッション管理
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# データベースURL（環境変数から取得、デフォルト値あり）
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://bid_user:bid_password_2024@postgres:5432/bid_kacho_db"
)

# SQLAlchemyエンジンの作成
engine = create_engine(DATABASE_URL)

# セッションローカルクラスの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラスの作成
Base = declarative_base()

def get_db():
    """
    データベースセッションを取得する依存関数
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()