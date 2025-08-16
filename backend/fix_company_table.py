#!/usr/bin/env python3
"""
companiesテーブルのスキーマを修正するスクリプト
"""

import os
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse

# 環境変数を読み込み
load_dotenv()

def fix_company_table():
    """companiesテーブルのスキーマを修正"""
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
        
        cursor = conn.cursor()
        
        # 既存のテーブルを削除して再作成
        print("Dropping existing companies table...")
        cursor.execute("DROP TABLE IF EXISTS companies CASCADE")
        
        print("Creating new companies table with correct schema...")
        cursor.execute("""
            CREATE TABLE companies (
                id SERIAL PRIMARY KEY,
                company_code VARCHAR(50) UNIQUE,
                company_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # デモユーザーを作成
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        print("Creating demo user...")
        cursor.execute("""
            INSERT INTO companies (company_code, company_name, email, password_hash, is_active) 
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, company_name, email
        """, ('DEMO001', 'デモ建設株式会社', 'demo@example.com', pwd_context.hash('demo123'), True))
        
        new_user = cursor.fetchone()
        conn.commit()
        print(f"Demo user created: ID={new_user[0]}, Name={new_user[1]}, Email={new_user[2]}")
        
        # テーブル構造を確認
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'companies'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print("\n=== Companies table structure ===")
        for col in columns:
            print(f"- {col[0]}: {col[1]}")
        
        cursor.close()
        conn.close()
        print("\nDatabase fix completed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    fix_company_table()