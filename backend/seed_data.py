#!/usr/bin/env python3
"""
Seed data script for Docker PostgreSQL
既存のCSV/JSONファイルからローカルのDockerPostgreSQLにデータを投入
"""
import os
import sys
import json
import csv
import psycopg2
from datetime import datetime
import pandas as pd
from pathlib import Path

# データベース接続設定（Docker環境用）
# 環境変数から取得、なければデフォルト値を使用
import os

if os.getenv('DATABASE_URL'):
    # DATABASE_URLが設定されている場合はそれを使用
    import re
    from urllib.parse import urlparse, unquote
    db_url = os.getenv('DATABASE_URL')
    parsed = urlparse(db_url)
    DB_CONFIG = {
        'user': parsed.username,
        'password': unquote(parsed.password) if parsed.password else None,
        'host': parsed.hostname,
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip('/').split('?')[0]  # Remove query params
    }
else:
    # ローカル開発用のデフォルト設定
    DB_CONFIG = {
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'bid_kacho_db',
        'user': 'bid_user',
        'password': 'bid_password_2024'
    }

# データファイルのパス
# Docker環境の場合は/tmp/dataを使用
if os.path.exists('/tmp/data'):
    DATA_DIR = Path('/tmp/data/raw')
else:
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data' / 'raw'

def get_connection():
    """PostgreSQL接続を取得"""
    return psycopg2.connect(**DB_CONFIG)

def create_tables(conn):
    """必要なテーブルを作成"""
    cursor = conn.cursor()
    
    # 公開中案件テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenders_open (
            tender_id VARCHAR(100) PRIMARY KEY,
            source VARCHAR(50),
            publisher VARCHAR(200),
            title VARCHAR(500),
            prefecture VARCHAR(50),
            municipality VARCHAR(100),
            address_text TEXT,
            use_type VARCHAR(100),
            method VARCHAR(100),
            jv_allowed BOOLEAN DEFAULT FALSE,
            floor_area_m2 DECIMAL(10, 2),
            bid_date DATE,
            notice_date DATE,
            estimated_price_jpy BIGINT,
            minimum_price_jpy BIGINT,
            origin_url TEXT,
            last_seen_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 落札結果テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS awards (
            award_id VARCHAR(100) PRIMARY KEY,
            tender_id VARCHAR(100),
            project_name VARCHAR(500),
            contractor VARCHAR(200),
            contractor_id VARCHAR(50),
            contract_amount BIGINT,
            contract_date DATE,
            participants_count INTEGER,
            prefecture VARCHAR(50),
            municipality VARCHAR(100),
            use_type VARCHAR(100),
            floor_area_m2 DECIMAL(10, 2),
            bid_method VARCHAR(100),
            evaluation_score DECIMAL(5, 2),
            price_score DECIMAL(5, 2),
            estimated_price BIGINT,
            win_rate DECIMAL(5, 2),
            jv_partner VARCHAR(200),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # インデックスの作成
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tenders_prefecture ON tenders_open(prefecture)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tenders_bid_date ON tenders_open(bid_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tenders_use_type ON tenders_open(use_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_awards_contractor ON awards(contractor)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_awards_prefecture ON awards(prefecture)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_awards_contract_date ON awards(contract_date)")
    
    conn.commit()
    print("✅ テーブル作成完了")

def load_tender_data(conn):
    """JSONファイルから公開中案件データを読み込み"""
    json_file = DATA_DIR / 'mock_tender_data_224560.json'
    
    if not json_file.exists():
        print(f"⚠️ ファイルが見つかりません: {json_file}")
        return
    
    print(f"📄 読み込み中: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cursor = conn.cursor()
    
    # 既存データをクリア
    cursor.execute("TRUNCATE TABLE tenders_open CASCADE")
    
    # データを挿入
    insert_query = """
        INSERT INTO tenders_open (
            tender_id, source, publisher, title, prefecture, municipality,
            address_text, use_type, method, jv_allowed, floor_area_m2,
            bid_date, notice_date, estimated_price_jpy, minimum_price_jpy,
            origin_url, last_seen_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON CONFLICT (tender_id) DO NOTHING
    """
    
    count = 0
    for item in data:
        try:
            cursor.execute(insert_query, (
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
            count += 1
            
            if count % 10000 == 0:
                conn.commit()
                print(f"  - {count:,} 件処理済み...")
        except Exception as e:
            print(f"エラー (tender_id: {item.get('tender_id')}): {e}")
            continue
    
    conn.commit()
    print(f"✅ 公開中案件データ {count:,} 件を投入完了")

def load_award_data(conn):
    """CSVファイルから落札結果データを読み込み"""
    cursor = conn.cursor()
    
    # 既存データをクリア
    cursor.execute("TRUNCATE TABLE awards CASCADE")
    
    # 星田建設株式会社の落札実績データを追加
    insert_hoshida_awards(cursor)
    
    # company_award_history.csv を読み込み
    csv_file1 = DATA_DIR / 'company_award_history.csv'
    if csv_file1.exists():
        print(f"📄 読み込み中: {csv_file1}")
        
        with open(csv_file1, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            insert_query = """
                INSERT INTO awards (
                    award_id, tender_id, project_name, contractor, contractor_id,
                    contract_amount, estimated_price, win_rate, contract_date,
                    participants_count, prefecture, municipality, use_type,
                    floor_area_m2, bid_method, evaluation_score, price_score, jv_partner
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (award_id) DO NOTHING
            """
            
            count = 0
            for row in reader:
                try:
                    cursor.execute(insert_query, (
                        row['award_id'],
                        row['tender_id'],
                        row['project_name'],
                        row['contractor'],
                        row.get('contractor_id'),
                        int(row['contract_amount']) if row['contract_amount'] else None,
                        int(row['estimated_price']) if row.get('estimated_price') else None,
                        float(row['win_rate']) if row.get('win_rate') else None,
                        row['contract_date'],
                        int(row['participants_count']) if row.get('participants_count') else None,
                        row['prefecture'],
                        row['municipality'],
                        row.get('use_type'),
                        float(row['floor_area_m2']) if row.get('floor_area_m2') else None,
                        row.get('bid_method'),
                        float(row['evaluation_score']) if row.get('evaluation_score') else None,
                        float(row['price_score']) if row.get('price_score') else None,
                        row.get('jv_partner')
                    ))
                    count += 1
                except Exception as e:
                    print(f"エラー (award_id: {row.get('award_id')}): {e}")
                    continue
            
            conn.commit()
            print(f"✅ company_award_history.csv から {count} 件を投入完了")
    
    # mock_award_data_2000.csv を読み込み
    csv_file2 = DATA_DIR / 'mock_award_data_2000.csv'
    if csv_file2.exists():
        print(f"📄 読み込み中: {csv_file2}")
        
        with open(csv_file2, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            insert_query = """
                INSERT INTO awards (
                    award_id, tender_id, project_name, contractor,
                    contract_amount, contract_date, participants_count,
                    prefecture, municipality, use_type, floor_area_m2,
                    bid_method, evaluation_score, price_score
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) ON CONFLICT (award_id) DO NOTHING
            """
            
            count = 0
            for row in reader:
                try:
                    cursor.execute(insert_query, (
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
                    count += 1
                except Exception as e:
                    print(f"エラー (award_id: {row.get('award_id')}): {e}")
                    continue
            
            conn.commit()
            print(f"✅ mock_award_data_2000.csv から {count} 件を投入完了")

def insert_hoshida_awards(cursor):
    """星田建設株式会社の落札実績データを挿入"""
    import random
    from datetime import datetime, timedelta
    
    print("📄 星田建設株式会社の落札実績データを生成中...")
    
    # 基準日
    base_date = datetime(2023, 1, 1)
    
    # 地域分布
    prefectures = {
        '東京都': {'count': 81, 'municipalities': ['千代田区', '港区', '新宿区', '渋谷区', '世田谷区', '目黒区', '品川区', '大田区', '江東区', '墨田区']},
        '神奈川県': {'count': 44, 'municipalities': ['横浜市', '川崎市', '相模原市', '横須賀市', '鎌倉市', '藤沢市', '茅ヶ崎市', '平塚市']},
        '埼玉県': {'count': 29, 'municipalities': ['さいたま市', '川口市', '所沢市', '春日部市', '越谷市', '草加市', '川越市']},
        '千葉県': {'count': 25, 'municipalities': ['千葉市', '船橋市', '市川市', '松戸市', '柏市', '市原市', '流山市']},
        '茨城県': {'count': 10, 'municipalities': ['水戸市', 'つくば市', '日立市', 'ひたちなか市', '土浦市']},
        '栃木県': {'count': 6, 'municipalities': ['宇都宮市', '小山市', '栃木市', '足利市']},
        '群馬県': {'count': 5, 'municipalities': ['前橋市', '高崎市', '太田市', '伊勢崎市']}
    }
    
    # 用途分布
    use_types = {
        '学校': {'count': 76, 'avg_amount': 850000000, 'avg_area': 4500},
        '庁舎': {'count': 55, 'avg_amount': 640000000, 'avg_area': 3800},
        '公民館': {'count': 28, 'avg_amount': 320000000, 'avg_area': 1800},
        '体育館': {'count': 22, 'avg_amount': 480000000, 'avg_area': 2800},
        '住宅': {'count': 12, 'avg_amount': 890000000, 'avg_area': 5200},
        '病院': {'count': 7, 'avg_amount': 1200000000, 'avg_area': 6500}
    }
    
    # 入札方式分布
    bid_methods = {
        '総合評価方式': 100,
        '一般競争入札': 80,
        '指名競争入札': 15,
        '随意契約': 5
    }
    
    award_id = 10000  # 開始ID
    total_count = 0
    
    insert_query = """
        INSERT INTO awards (
            award_id, tender_id, project_name, contractor,
            contract_amount, contract_date, participants_count,
            prefecture, municipality, use_type, floor_area_m2,
            bid_method, evaluation_score, price_score, estimated_price, win_rate
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON CONFLICT (award_id) DO NOTHING
    """
    
    # 各地域ごとにデータを生成
    for prefecture, pref_data in prefectures.items():
        municipalities = pref_data['municipalities']
        pref_count = pref_data['count']
        
        for i in range(pref_count):
            municipality = random.choice(municipalities)
            
            # 用途を選択（確率分布に基づく）
            use_type_choices = []
            for use, use_data in use_types.items():
                use_type_choices.extend([use] * use_data['count'])
            use_type = random.choice(use_type_choices)
            use_data = use_types[use_type]
            
            # 入札方式を選択
            method_choices = []
            for method, count in bid_methods.items():
                method_choices.extend([method] * count)
            bid_method = random.choice(method_choices)
            
            # プロジェクト名を生成
            if use_type == '学校':
                school_types = ['小学校', '中学校', '高等学校']
                school_type = random.choice(school_types)
                project_types = ['改築工事', '耐震補強工事', '大規模改修工事', '増築工事']
                project_name = f"{municipality}立第{random.randint(1, 10)}{school_type}{random.choice(project_types)}"
            elif use_type == '庁舎':
                project_types = ['新築工事', '改修工事', '耐震補強工事', '増築工事']
                project_name = f"{municipality}庁舎{random.choice(project_types)}"
            elif use_type == '公民館':
                project_types = ['新築工事', '改修工事', '大規模修繕工事']
                project_name = f"{municipality}{random.choice(['中央', '北', '南', '東', '西'])}公民館{random.choice(project_types)}"
            elif use_type == '体育館':
                project_types = ['新築工事', '改修工事', '大規模改修工事']
                project_name = f"{municipality}総合体育館{random.choice(project_types)}"
            elif use_type == '住宅':
                project_name = f"{municipality}営住宅{random.randint(1, 20)}号棟建設工事"
            else:  # 病院
                project_name = f"{municipality}立病院{random.choice(['新築', '増築', '改修'])}工事"
            
            # 契約金額（平均値を中心に±30%の範囲でランダム）
            avg_amount = use_data['avg_amount']
            contract_amount = int(avg_amount * random.uniform(0.7, 1.3))
            
            # 予定価格（契約金額の105-115%）
            estimated_price = int(contract_amount * random.uniform(1.05, 1.15))
            
            # 落札率
            win_rate = (contract_amount / estimated_price) * 100
            
            # 延床面積
            floor_area = use_data['avg_area'] * random.uniform(0.6, 1.4)
            
            # 契約日（過去2年間でランダム）
            days_ago = random.randint(1, 730)
            contract_date = base_date - timedelta(days=days_ago)
            
            # 参加者数
            if bid_method == '総合評価方式':
                participants = random.randint(5, 15)
            elif bid_method == '一般競争入札':
                participants = random.randint(8, 20)
            elif bid_method == '指名競争入札':
                participants = random.randint(3, 8)
            else:  # 随意契約
                participants = 1
            
            # 評価スコア（総合評価方式の場合）
            if bid_method == '総合評価方式':
                evaluation_score = random.uniform(75, 95)
                price_score = random.uniform(70, 90)
            else:
                evaluation_score = None
                price_score = None
            
            # データ挿入
            cursor.execute(insert_query, (
                f'hoshida-{award_id}',
                f'tender-hoshida-{award_id}',
                project_name,
                '星田建設株式会社',
                contract_amount,
                contract_date.strftime('%Y-%m-%d'),
                participants,
                prefecture,
                municipality,
                use_type,
                floor_area,
                bid_method,
                evaluation_score,
                price_score,
                estimated_price,
                win_rate
            ))
            
            award_id += 1
            total_count += 1
    
    print(f"✅ 星田建設株式会社の落札実績 {total_count} 件を投入完了")
    print(f"   - 地域分布: 東京{prefectures['東京都']['count']}件, 神奈川{prefectures['神奈川県']['count']}件, 埼玉{prefectures['埼玉県']['count']}件, 千葉{prefectures['千葉県']['count']}件")
    print(f"   - 用途分布: 学校{use_types['学校']['count']}件, 庁舎{use_types['庁舎']['count']}件, 公民館{use_types['公民館']['count']}件")
    print(f"   - 入札方式: 総合評価{bid_methods['総合評価方式']}件, 一般競争{bid_methods['一般競争入札']}件")

def verify_data(conn):
    """投入されたデータを検証"""
    cursor = conn.cursor()
    
    # テーブルごとの件数を確認
    tables = ['tenders_open', 'awards', 'companies', 'company_awards']
    
    print("\n📊 データ投入結果:")
    print("-" * 50)
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:20} : {count:,} 件")
        except Exception as e:
            print(f"{table:20} : テーブルが存在しません")
    
    # サンプルデータを表示
    print("\n📋 サンプルデータ (tenders_open):")
    cursor.execute("""
        SELECT tender_id, title, prefecture, bid_date 
        FROM tenders_open 
        LIMIT 3
    """)
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1][:30]}... ({row[2]}, {row[3]})")
    
    print("\n📋 サンプルデータ (awards):")
    cursor.execute("""
        SELECT award_id, project_name, contractor, contract_date 
        FROM awards 
        LIMIT 3
    """)
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1][:30]}... ({row[2]}, {row[3]})")

def main():
    """メイン処理"""
    print("🚀 Seedデータ投入開始")
    print(f"📁 データディレクトリ: {DATA_DIR}")
    print("-" * 50)
    
    try:
        # データベース接続
        conn = get_connection()
        print("✅ データベース接続成功")
        
        # テーブル作成
        create_tables(conn)
        
        # データ投入
        load_tender_data(conn)
        load_award_data(conn)
        
        # データ検証
        verify_data(conn)
        
        print("\n✨ Seedデータ投入完了!")
        
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()