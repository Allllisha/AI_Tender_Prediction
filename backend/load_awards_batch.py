#!/usr/bin/env python3
"""
落札データをバッチ処理でAzure PostgreSQLに投入
"""
import csv
import psycopg2
from psycopg2.extras import execute_batch
import os

DATABASE_URL = 'postgresql://dbadmin:Password2024@postgres-bid-kacho.postgres.database.azure.com:5432/bid_kacho_db?sslmode=require'

def load_awards_batch():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    csv_file = '/Users/anemoto/bid_kacho/data/raw/mock_award_data_2000.csv'
    
    print(f"Loading {csv_file}...")
    
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        # バッチ用のデータを準備
        batch_data = []
        for row in reader:
            batch_data.append((
                row['award_id'],
                row['tender_id'],
                row['project_name'],
                row['contractor'],
                int(row['contract_amount']) if row['contract_amount'] else None,
                row['contract_date'],
                int(row['participants_count']) if row['participants_count'] else None,
                row['prefecture'],
                row['municipality'],
                row['use_type'],
                float(row['floor_area_m2']) if row['floor_area_m2'] else None,
                row['bid_method'],
                float(row['evaluation_score']) if row.get('evaluation_score') else None,
                float(row['price_score']) if row.get('price_score') else None
            ))
            
            # 100件ごとにバッチ挿入
            if len(batch_data) >= 100:
                execute_batch(cursor, """
                    INSERT INTO awards (
                        award_id, tender_id, project_name, contractor,
                        contract_amount, contract_date, participants_count,
                        prefecture, municipality, use_type, floor_area_m2,
                        bid_method, evaluation_score, price_score
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (award_id) DO NOTHING
                """, batch_data)
                conn.commit()
                print(f"  Inserted {len(batch_data)} records...")
                batch_data = []
        
        # 残りのデータを挿入
        if batch_data:
            execute_batch(cursor, """
                INSERT INTO awards (
                    award_id, tender_id, project_name, contractor,
                    contract_amount, contract_date, participants_count,
                    prefecture, municipality, use_type, floor_area_m2,
                    bid_method, evaluation_score, price_score
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (award_id) DO NOTHING
            """, batch_data)
            conn.commit()
            print(f"  Inserted final {len(batch_data)} records")
    
    # 結果確認
    cursor.execute("SELECT COUNT(*) FROM awards")
    total = cursor.fetchone()[0]
    print(f"\n✅ Total awards in database: {total} records")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    load_awards_batch()