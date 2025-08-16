#!/usr/bin/env python3
"""
デモユーザーの会社名を星田建設株式会社に更新するスクリプト
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

def update_demo_user():
    """デモユーザーの会社名を更新"""
    # データベース接続
    database_url = os.getenv('DATABASE_URL', 'postgresql://bid_user:bid_password_2024@127.0.0.1:5432/bid_kacho_db')
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # デモユーザーの会社名を更新
        cursor.execute("""
            UPDATE companies 
            SET company_name = '星田建設株式会社' 
            WHERE email = 'demo@example.com'
        """)
        
        affected_rows = cursor.rowcount
        conn.commit()
        
        if affected_rows > 0:
            print("✅ デモユーザーの会社名を「星田建設株式会社」に更新しました")
            
            # 確認
            cursor.execute("SELECT company_name, email FROM companies WHERE email = 'demo@example.com'")
            result = cursor.fetchone()
            if result:
                print(f"   会社名: {result[0]}")
                print(f"   メール: {result[1]}")
        else:
            print("⚠️ デモユーザーが見つかりませんでした")
            
            # 全ユーザーを表示
            cursor.execute("SELECT company_name, email FROM companies")
            companies = cursor.fetchall()
            print("\n現在登録されている会社:")
            for company in companies:
                print(f"  - {company[0]} ({company[1]})")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_demo_user()