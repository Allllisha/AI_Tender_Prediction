#!/usr/bin/env python3
"""
open_tendersテーブルにデータを投入するスクリプト
"""

import os
import json
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

def load_open_tender_data(conn):
    """公開入札データをロード（JSONファイルから）"""
    cursor = conn.cursor()
    
    # JSONファイルを読み込み
    json_path = '../data/raw/mock_tender_data_224560.json'
    
    if not os.path.exists(json_path):
        print(f"Error: Open tender data file not found at {json_path}")
        return
    
    print(f"Loading data from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        tender_data = json.load(f)
    
    print(f"Found {len(tender_data)} tender records")
    
    # バッチサイズを設定（一度に処理するレコード数）
    batch_size = 1000
    total_inserted = 0
    
    for i in range(0, len(tender_data), batch_size):
        batch = tender_data[i:i+batch_size]
        data = []
        
        for item in batch:
            data.append((
                item.get('tender_id'),
                item.get('title'),
                item.get('publisher'),
                item.get('prefecture'),
                item.get('municipality'),
                item.get('address_text'),
                item.get('use'),  # JSONでは'use'というキー名
                item.get('method'),
                float(item.get('floor_area_m2', 0)) if item.get('floor_area_m2') else None,
                pd.to_datetime(item.get('bid_date')).date() if item.get('bid_date') else None,
                pd.to_datetime(item.get('notice_date')).date() if item.get('notice_date') else None,
                int(item.get('estimated_price_jpy', 0)) if item.get('estimated_price_jpy') else None,
                int(item.get('minimum_price_jpy', 0)) if item.get('minimum_price_jpy') else None,
                bool(item.get('jv_allowed', False)),
                item.get('origin_url')
            ))
        
        # バルクインサート
        query = """
            INSERT INTO open_tenders (
                tender_id, title, publisher, prefecture, municipality,
                address, use_type, bid_method, floor_area_m2, bid_date,
                notice_date, estimated_price, minimum_price, jv_allowed, origin_url
            ) VALUES %s
            ON CONFLICT (tender_id) DO NOTHING
        """
        
        execute_values(cursor, query, data)
        conn.commit()
        
        total_inserted += len(data)
        print(f"Inserted batch {i//batch_size + 1}: {len(data)} records (Total: {total_inserted})")
    
    print(f"\nSuccessfully loaded {total_inserted} open tender records")

def main():
    """メイン処理"""
    try:
        # データベースに接続
        conn = get_db_connection()
        print("Connected to Azure PostgreSQL database")
        
        # 現在のレコード数を確認
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM open_tenders")
        before_count = cursor.fetchone()[0]
        print(f"Current records in open_tenders: {before_count}")
        
        # データをロード
        load_open_tender_data(conn)
        
        # 最終的なレコード数を確認
        cursor.execute("SELECT COUNT(*) FROM open_tenders")
        after_count = cursor.fetchone()[0]
        print(f"\nFinal records in open_tenders: {after_count}")
        print(f"New records added: {after_count - before_count}")
        
        # 接続を閉じる
        conn.close()
        print("\nDatabase update completed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()