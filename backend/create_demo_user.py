#!/usr/bin/env python3
"""
デモユーザーを作成するスクリプト
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth import get_password_hash
from models import Company, Base
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def create_demo_user():
    """デモユーザーを作成"""
    # データベース接続
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL environment variable is not set")
        sys.exit(1)
    
    # SQLAlchemyエンジンを作成
    engine = create_engine(database_url)
    
    # テーブルが存在しない場合は作成
    Base.metadata.create_all(bind=engine)
    
    # セッションを作成
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 既存のデモユーザーを確認
        existing_user = db.query(Company).filter(Company.email == "demo@example.com").first()
        
        if existing_user:
            print("Demo user already exists. Updating password...")
            existing_user.password_hash = get_password_hash("demo123")
            existing_user.is_active = True
            db.commit()
            print(f"Demo user updated: {existing_user.email}")
        else:
            # デモユーザーを作成
            demo_user = Company(
                name="デモ建設株式会社",
                email="demo@example.com",
                password_hash=get_password_hash("demo123"),
                is_active=True
            )
            
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            
            print(f"Demo user created successfully!")
            print(f"Email: {demo_user.email}")
            print(f"Password: demo123")
            print(f"Company: {demo_user.name}")
            print(f"ID: {demo_user.id}")
        
        # 確認のため全てのユーザーを表示
        print("\n=== All registered companies ===")
        companies = db.query(Company).all()
        for company in companies:
            print(f"- {company.name} ({company.email}) - Active: {company.is_active}")
            
    except Exception as e:
        print(f"Error creating demo user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_user()