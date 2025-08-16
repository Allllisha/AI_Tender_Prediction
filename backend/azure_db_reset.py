#!/usr/bin/env python3
"""
Azure PostgreSQLデータベースを完全にリセットしてシードデータを投入するスクリプト
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def reset_azure_database():
    """Azure PostgreSQLのテーブルを全て削除して再作成"""
    
    # Azure PostgreSQL接続情報
    DATABASE_URL = "postgresql://dbadmin:Password2024@postgres-bid-kacho.postgres.database.azure.com:5432/bid_kacho_db?sslmode=require"
    
    print("🗑️  Cleaning up Azure PostgreSQL database...")
    print("=" * 50)
    
    try:
        # データベースに接続
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("📋 Dropping existing tables...")
        
        # 依存関係を考慮して、外部キー制約のあるテーブルから削除
        tables_to_drop = [
            'csv_upload_history',
            'company_awards', 
            'awards',
            'tenders_open',
            'companies'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                print(f"  ✅ Dropped table: {table}")
            except Exception as e:
                print(f"  ⚠️ Could not drop table {table}: {e}")
        
        # その他の可能性のあるテーブルも削除
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
        """)
        
        other_tables = cursor.fetchall()
        for (table,) in other_tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
                print(f"  ✅ Dropped additional table: {table}")
            except Exception as e:
                print(f"  ⚠️ Could not drop table {table}: {e}")
        
        print("\n✅ Database cleanup completed")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during database cleanup: {e}")
        return False

def main():
    """メイン処理"""
    print("🚀 Azure PostgreSQL Database Reset Script")
    print("=" * 50)
    print("⚠️  WARNING: This will DELETE ALL DATA in the Azure database!")
    print("=" * 50)
    
    # 確認プロンプト
    response = input("\nAre you sure you want to continue? Type 'YES' to confirm: ")
    if response != 'YES':
        print("❌ Operation cancelled")
        sys.exit(0)
    
    # データベースをリセット
    if reset_azure_database():
        print("\n" + "=" * 50)
        print("✅ Database reset successful!")
        print("\n📌 Next steps:")
        print("1. Run the seed data script:")
        print("   export DATABASE_URL='postgresql://dbadmin:Password2024@postgres-bid-kacho.postgres.database.azure.com:5432/bid_kacho_db?sslmode=require'")
        print("   python seed_data_azure.py")
    else:
        print("\n❌ Database reset failed")
        sys.exit(1)

if __name__ == "__main__":
    main()