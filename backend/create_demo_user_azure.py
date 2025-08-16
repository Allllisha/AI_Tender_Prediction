#!/usr/bin/env python3
"""
Azure PostgreSQLにデモユーザーを直接作成するスクリプト
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from passlib.context import CryptContext
from dotenv import load_dotenv
from urllib.parse import urlparse

# 環境変数を読み込み
load_dotenv()

# パスワードハッシュ化
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """パスワードのハッシュ化"""
    return pwd_context.hash(password)

def create_demo_user():
    """デモユーザーを作成"""
    # データベース接続
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("DATABASE_URL environment variable is not set")
        return
    
    print(f"Connecting to database...")
    
    # DATABASE_URLをパース
    parsed = urlparse(database_url)
    
    try:
        # PostgreSQLに接続
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password,
            sslmode='require'
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # companiesテーブルが存在するか確認
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'companies'
            );
        """)
        table_exists = cursor.fetchone()['exists']
        
        if not table_exists:
            print("Creating companies table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("Companies table created successfully")
        
        # 既存のデモユーザーを確認
        cursor.execute("""
            SELECT id, email, name FROM companies WHERE email = %s
        """, ('demo@example.com',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"Demo user already exists: {existing_user}")
            # パスワードを更新
            cursor.execute("""
                UPDATE companies 
                SET password_hash = %s, is_active = TRUE 
                WHERE email = %s
            """, (get_password_hash('demo123'), 'demo@example.com'))
            conn.commit()
            print("Demo user password updated")
        else:
            # デモユーザーを作成
            cursor.execute("""
                INSERT INTO companies (name, email, password_hash, is_active) 
                VALUES (%s, %s, %s, %s)
                RETURNING id, name, email
            """, ('デモ建設株式会社', 'demo@example.com', get_password_hash('demo123'), True))
            
            new_user = cursor.fetchone()
            conn.commit()
            print(f"Demo user created successfully: {new_user}")
        
        # 全ユーザーを確認
        cursor.execute("""
            SELECT id, name, email, is_active, created_at 
            FROM companies 
            ORDER BY id
        """)
        all_users = cursor.fetchall()
        
        print("\n=== All registered companies ===")
        for user in all_users:
            print(f"ID: {user['id']}, Name: {user['name']}, Email: {user['email']}, Active: {user['is_active']}, Created: {user['created_at']}")
        
        cursor.close()
        conn.close()
        print("\nDatabase connection closed")
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    create_demo_user()