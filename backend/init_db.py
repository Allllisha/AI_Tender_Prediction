#!/usr/bin/env python3
"""
Azure PostgreSQL データベースの初期化スクリプト
テーブル作成とデータ投入を行う
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

def create_tables(conn):
    """テーブルを作成"""
    cursor = conn.cursor()
    
    # 既存のテーブルを削除（開発用）
    cursor.execute("DROP TABLE IF EXISTS awards CASCADE")
    cursor.execute("DROP TABLE IF EXISTS open_tenders CASCADE")
    
    # awardsテーブルを作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS awards (
            id SERIAL PRIMARY KEY,
            tender_id VARCHAR(255),
            project_name TEXT,
            publisher VARCHAR(255),
            prefecture VARCHAR(100),
            municipality VARCHAR(100),
            address TEXT,
            use_type VARCHAR(100),
            method VARCHAR(100),
            floor_area_m2 FLOAT,
            award_date DATE,
            contractor VARCHAR(255),
            award_amount_jpy BIGINT,
            estimated_price_jpy BIGINT,
            win_rate FLOAT,
            participants_count INTEGER,
            technical_score FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # open_tendersテーブルを作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS open_tenders (
            id SERIAL PRIMARY KEY,
            tender_id VARCHAR(255) UNIQUE,
            title TEXT,
            publisher VARCHAR(255),
            prefecture VARCHAR(100),
            municipality VARCHAR(100),
            address TEXT,
            use_type VARCHAR(100),
            bid_method VARCHAR(100),
            floor_area_m2 FLOAT,
            bid_date DATE,
            notice_date DATE,
            estimated_price BIGINT,
            minimum_price BIGINT,
            jv_allowed BOOLEAN,
            origin_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # インデックスを作成
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_awards_prefecture ON awards(prefecture)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_awards_use_type ON awards(use_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_awards_award_date ON awards(award_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_open_tenders_prefecture ON open_tenders(prefecture)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_open_tenders_bid_date ON open_tenders(bid_date)")
    
    conn.commit()
    print("Tables created successfully")

def load_award_data(conn):
    """落札データをロード"""
    cursor = conn.cursor()
    
    # CSVファイルを読み込み
    csv_path = '/app/data/raw/mock_award_data_2000.csv'
    if not os.path.exists(csv_path):
        csv_path = '../data/raw/mock_award_data_2000.csv'
    
    if not os.path.exists(csv_path):
        print(f"Warning: Award data file not found at {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    
    # データを準備
    data = []
    for _, row in df.iterrows():
        data.append((
            row.get('tender_id'),
            row.get('project_name'),
            row.get('publisher'),
            row.get('prefecture'),
            row.get('municipality'),
            row.get('address'),
            row.get('use_type'),
            row.get('method'),
            float(row.get('floor_area_m2', 0)) if pd.notna(row.get('floor_area_m2')) else None,
            pd.to_datetime(row.get('award_date')).date() if pd.notna(row.get('award_date')) else None,
            row.get('contractor'),
            int(row.get('award_amount_jpy', 0)) if pd.notna(row.get('award_amount_jpy')) else None,
            int(row.get('estimated_price_jpy', 0)) if pd.notna(row.get('estimated_price_jpy')) else None,
            float(row.get('win_rate', 0)) if pd.notna(row.get('win_rate')) else None,
            int(row.get('participants_count', 0)) if pd.notna(row.get('participants_count')) else None,
            float(row.get('technical_score', 0)) if pd.notna(row.get('technical_score')) else None
        ))
    
    # バルクインサート
    query = """
        INSERT INTO awards (
            tender_id, project_name, publisher, prefecture, municipality,
            address, use_type, method, floor_area_m2, award_date,
            contractor, award_amount_jpy, estimated_price_jpy, win_rate,
            participants_count, technical_score
        ) VALUES %s
    """
    
    execute_values(cursor, query, data)
    conn.commit()
    print(f"Loaded {len(data)} award records")

def load_open_tender_data(conn):
    """公開入札データをロード（JSONファイルから）"""
    cursor = conn.cursor()
    
    # JSONファイルを読み込み
    json_path = '/app/data/raw/mock_tender_data_224560.json'
    if not os.path.exists(json_path):
        json_path = '../data/raw/mock_tender_data_224560.json'
    
    if not os.path.exists(json_path):
        print(f"Warning: Open tender data file not found at {json_path}")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        tender_data = json.load(f)
    
    # データを準備
    data = []
    for item in tender_data:
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
    print(f"Loaded {len(data)} open tender records")

def load_company_award_history(conn):
    """企業の落札履歴データをロード"""
    cursor = conn.cursor()
    
    # CSVファイルを読み込み
    csv_path = '/app/data/raw/company_award_history.csv'
    if not os.path.exists(csv_path):
        csv_path = '../data/raw/company_award_history.csv'
    
    if not os.path.exists(csv_path):
        print(f"Warning: Company award history file not found at {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    
    # awardsテーブルにデータを追加（company_award_historyは落札実績データ）
    data = []
    for _, row in df.iterrows():
        data.append((
            row.get('tender_id'),
            row.get('project_name'),
            row.get('publisher'),
            row.get('prefecture'),
            row.get('municipality'),
            row.get('address'),
            row.get('use_type'),
            row.get('method'),
            float(row.get('floor_area_m2', 0)) if pd.notna(row.get('floor_area_m2')) else None,
            pd.to_datetime(row.get('award_date')).date() if pd.notna(row.get('award_date')) else None,
            row.get('contractor', '星田建設株式会社'),  # デフォルトで自社名を設定
            int(row.get('award_amount_jpy', 0)) if pd.notna(row.get('award_amount_jpy')) else None,
            int(row.get('estimated_price_jpy', 0)) if pd.notna(row.get('estimated_price_jpy')) else None,
            float(row.get('win_rate', 0)) if pd.notna(row.get('win_rate')) else None,
            int(row.get('participants_count', 0)) if pd.notna(row.get('participants_count')) else None,
            float(row.get('technical_score', 0)) if pd.notna(row.get('technical_score')) else None
        ))
    
    # バルクインサート
    query = """
        INSERT INTO awards (
            tender_id, project_name, publisher, prefecture, municipality,
            address, use_type, method, floor_area_m2, award_date,
            contractor, award_amount_jpy, estimated_price_jpy, win_rate,
            participants_count, technical_score
        ) VALUES %s
    """
    
    execute_values(cursor, query, data)
    conn.commit()
    print(f"Loaded {len(data)} company award history records")

def main():
    """メイン処理"""
    try:
        # データベースに接続
        conn = get_db_connection()
        print("Connected to database")
        
        # テーブルを作成
        create_tables(conn)
        
        # データをロード
        print("\nLoading mock award data...")
        load_award_data(conn)
        
        print("\nLoading company award history...")
        load_company_award_history(conn)
        
        print("\nLoading open tender data...")
        load_open_tender_data(conn)
        
        # 統計情報を表示
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM awards")
        award_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM open_tenders")
        tender_count = cursor.fetchone()[0]
        
        print(f"\n=== Database Statistics ===")
        print(f"Total awards: {award_count}")
        print(f"Total open tenders: {tender_count}")
        
        # 接続を閉じる
        conn.close()
        print("\nDatabase initialization completed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()