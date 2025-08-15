#!/usr/bin/env python3
"""
company_award_history.csvをデータベースに投入するスクリプト
"""

import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from urllib.parse import urlparse

# 環境変数を読み込み
load_dotenv()

def get_db_connection():
    """データベース接続を取得"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # DATABASE_URLをパース
    parsed = urlparse(database_url)
    
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip('/'),
        user=parsed.username,
        password=parsed.password,
        sslmode='require'
    )
    return conn

def load_company_awards(conn):
    """company_award_history.csvをロード"""
    cursor = conn.cursor()
    
    # CSVファイルを読み込み
    csv_path = '../data/raw/company_award_history.csv'
    
    if not os.path.exists(csv_path):
        print(f"Error: Company award history file not found at {csv_path}")
        return
    
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path, encoding='utf-8-sig')  # BOM付きUTF-8に対応
    
    print(f"Found {len(df)} company award records")
    print(f"Columns: {df.columns.tolist()}")
    
    # データを準備
    data = []
    for _, row in df.iterrows():
        # 日付の処理
        award_date = None
        if pd.notna(row.get('contract_date')):
            try:
                award_date = pd.to_datetime(row['contract_date']).date()
            except:
                pass
        
        data.append((
            row.get('tender_id'),
            row.get('project_name'),
            None,  # publisher (CSVにない)
            row.get('prefecture'),
            row.get('municipality'),
            None,  # address (CSVにない)
            row.get('use_type'),
            row.get('bid_method', row.get('method')),
            float(row.get('floor_area_m2', 0)) if pd.notna(row.get('floor_area_m2')) else None,
            award_date,
            row.get('contractor', '星田建設株式会社'),
            int(row.get('contract_amount', 0)) if pd.notna(row.get('contract_amount')) else None,
            int(row.get('estimated_price', 0)) if pd.notna(row.get('estimated_price')) else None,
            float(row.get('win_rate', 0)) if pd.notna(row.get('win_rate')) else None,
            int(row.get('participants_count', 0)) if pd.notna(row.get('participants_count')) else None,
            float(row.get('evaluation_score', row.get('technical_score', 0))) if pd.notna(row.get('evaluation_score', row.get('technical_score'))) else None
        ))
    
    # バルクインサート
    query = """
        INSERT INTO awards (
            tender_id, project_name, publisher, prefecture, municipality,
            address, use_type, method, floor_area_m2, award_date,
            contractor, award_amount_jpy, estimated_price_jpy, win_rate,
            participants_count, technical_score
        ) VALUES %s
        ON CONFLICT DO NOTHING
    """
    
    execute_values(cursor, query, data)
    conn.commit()
    print(f"Successfully loaded {len(data)} company award records")

def main():
    """メイン処理"""
    try:
        # データベースに接続
        conn = get_db_connection()
        print("Connected to Azure PostgreSQL database")
        
        # 現在のレコード数を確認
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM awards")
        before_count = cursor.fetchone()[0]
        print(f"Current records in awards: {before_count}")
        
        # 星田建設のレコード数を確認
        cursor.execute("SELECT COUNT(*) FROM awards WHERE contractor = '星田建設株式会社'")
        company_before = cursor.fetchone()[0]
        print(f"Current 星田建設 records: {company_before}")
        
        # データをロード
        load_company_awards(conn)
        
        # 最終的なレコード数を確認
        cursor.execute("SELECT COUNT(*) FROM awards")
        after_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM awards WHERE contractor = '星田建設株式会社'")
        company_after = cursor.fetchone()[0]
        
        print(f"\n=== Final Statistics ===")
        print(f"Total awards: {after_count}")
        print(f"New records added: {after_count - before_count}")
        print(f"星田建設 records: {company_after}")
        print(f"New 星田建設 records: {company_after - company_before}")
        
        # 接続を閉じる
        conn.close()
        print("\nDatabase update completed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()