#!/usr/bin/env python3
"""
Azure PostgreSQLに完全なシードデータをデプロイするスクリプト
1. 既存のテーブルを全て削除
2. 新しいテーブルを作成
3. シードデータを投入
"""
import os
import sys

# 環境変数を設定
os.environ['DATABASE_URL'] = 'postgresql://dbadmin:Password2024@postgres-bid-kacho.postgres.database.azure.com:5432/bid_kacho_db?sslmode=require'
os.environ['DATA_DIR'] = '/Users/anemoto/bid_kacho/data/raw'

# azure_db_reset.pyの処理を実行
print("=" * 70)
print("STEP 1: Resetting Azure PostgreSQL Database")
print("=" * 70)

from azure_db_reset import reset_azure_database

if not reset_azure_database():
    print("❌ Failed to reset database")
    sys.exit(1)

print("\n" + "=" * 70)
print("STEP 2: Loading Seed Data")
print("=" * 70)

# seed_data_azure.pyを実行
from seed_data_azure import main as seed_main

try:
    seed_main()
    print("\n" + "=" * 70)
    print("✅ Azure PostgreSQL deployment completed successfully!")
    print("=" * 70)
except Exception as e:
    print(f"❌ Error during seed data loading: {e}")
    sys.exit(1)