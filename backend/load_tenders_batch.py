#!/usr/bin/env python3
"""
入札データをバッチ処理でAzure PostgreSQLに投入
"""
import json
import psycopg2
from psycopg2.extras import execute_batch
import os

DATABASE_URL = 'postgresql://dbadmin:Password2024@postgres-bid-kacho.postgres.database.azure.com:5432/bid_kacho_db?sslmode=require'

def load_tenders_batch():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    json_file = '/Users/anemoto/bid_kacho/data/raw/mock_tender_data_224560.json'
    
    print(f"Loading {json_file}...")
    print("This may take several minutes due to the large data size (224,552 records)...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} records from JSON file")
    
    # バッチ用のデータを準備
    batch_data = []
    count = 0
    
    for item in data:
        batch_data.append((
            item.get('tender_id'),
            item.get('source'),
            item.get('publisher'),
            item.get('title'),
            item.get('prefecture'),
            item.get('municipality'),
            item.get('address_text'),
            item.get('use'),
            item.get('method'),
            item.get('jv_allowed', False),
            item.get('floor_area_m2'),
            item.get('bid_date'),
            item.get('notice_date'),
            item.get('estimated_price_jpy'),
            item.get('minimum_price_jpy'),
            item.get('origin_url'),
            item.get('last_seen_at')
        ))
        
        # 1000件ごとにバッチ挿入
        if len(batch_data) >= 1000:
            execute_batch(cursor, """
                INSERT INTO tenders_open (
                    tender_id, source, publisher, title, prefecture, municipality,
                    address_text, use_type, method, jv_allowed, floor_area_m2,
                    bid_date, notice_date, estimated_price_jpy, minimum_price_jpy,
                    origin_url, last_seen_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tender_id) DO NOTHING
            """, batch_data, page_size=100)
            
            count += len(batch_data)
            conn.commit()
            
            if count % 10000 == 0:
                print(f"  Processed {count:,} records...")
            
            batch_data = []
    
    # 残りのデータを挿入
    if batch_data:
        execute_batch(cursor, """
            INSERT INTO tenders_open (
                tender_id, source, publisher, title, prefecture, municipality,
                address_text, use_type, method, jv_allowed, floor_area_m2,
                bid_date, notice_date, estimated_price_jpy, minimum_price_jpy,
                origin_url, last_seen_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (tender_id) DO NOTHING
        """, batch_data, page_size=100)
        count += len(batch_data)
        conn.commit()
        print(f"  Processed final {len(batch_data)} records")
    
    # 結果確認
    cursor.execute("SELECT COUNT(*) FROM tenders_open")
    total = cursor.fetchone()[0]
    print(f"\n✅ Total tenders in database: {total:,} records")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    load_tenders_batch()