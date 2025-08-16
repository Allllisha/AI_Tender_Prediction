#!/usr/bin/env python3
"""
open_tendersテーブルにサンプルデータを投入するスクリプト
"""

import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from urllib.parse import urlparse, unquote
from datetime import datetime, timedelta
import random

# 環境変数を読み込み
load_dotenv()

def get_db_connection():
    """データベース接続を取得"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # DATABASE_URLをパース
    parsed = urlparse(database_url)
    
    # パスワードをデコード
    password = unquote(parsed.password) if parsed.password else None
    
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        database=parsed.path.lstrip('/'),
        user=parsed.username,
        password=password,
        sslmode='require'
    )
    return conn

def populate_sample_tenders(conn):
    """サンプル入札データを投入"""
    cursor = conn.cursor()
    
    # まず既存のテストデータをクリア
    cursor.execute("DELETE FROM open_tenders WHERE tender_id LIKE 'tender_id%' OR tender_id LIKE 'SAMPLE-%'")
    
    # サンプルデータを作成
    sample_tenders = []
    
    prefectures = ["東京都", "神奈川県", "千葉県", "埼玉県", "大阪府", "愛知県", "福岡県"]
    municipalities = {
        "東京都": ["千代田区", "港区", "新宿区", "渋谷区", "世田谷区", "品川区", "目黒区"],
        "神奈川県": ["横浜市", "川崎市", "相模原市", "藤沢市", "鎌倉市", "厚木市", "小田原市"],
        "千葉県": ["千葉市", "船橋市", "松戸市", "市川市", "柏市", "流山市", "浦安市"],
        "埼玉県": ["さいたま市", "川口市", "川越市", "所沢市", "春日部市", "上尾市", "草加市"],
        "大阪府": ["大阪市", "堺市", "東大阪市", "豊中市", "吹田市", "高槻市", "枚方市"],
        "愛知県": ["名古屋市", "豊田市", "岡崎市", "一宮市", "豊橋市", "春日井市", "安城市"],
        "福岡県": ["福岡市", "北九州市", "久留米市", "飯塚市", "大牟田市", "春日市", "筑紫野市"]
    }
    
    use_types = ["学校", "庁舎", "病院", "図書館", "体育館", "文化施設", "福祉施設"]
    bid_methods = ["一般競争入札", "指名競争入札", "総合評価方式", "プロポーザル方式"]
    
    project_templates = [
        "{}改築工事",
        "{}新築工事",
        "{}増築工事",
        "{}耐震補強工事",
        "{}大規模改修工事",
        "{}外壁改修工事",
        "{}空調設備更新工事"
    ]
    
    # 100件のサンプルデータを生成
    base_date = datetime.now()
    
    for i in range(100):
        prefecture = random.choice(prefectures)
        municipality = random.choice(municipalities[prefecture])
        use_type = random.choice(use_types)
        bid_method = random.choice(bid_methods)
        project_template = random.choice(project_templates)
        
        # プロジェクト名を生成
        facility_names = {
            "学校": ["第一小学校", "第二小学校", "中央中学校", "北高等学校", "南中学校"],
            "庁舎": ["市役所本庁舎", "区役所", "支所", "市民センター", "行政センター"],
            "病院": ["市立病院", "総合医療センター", "中央病院", "救急医療センター"],
            "図書館": ["中央図書館", "市立図書館", "地域図書館", "こども図書館"],
            "体育館": ["総合体育館", "市民体育館", "スポーツセンター", "武道館"],
            "文化施設": ["文化会館", "市民会館", "芸術センター", "コンサートホール"],
            "福祉施設": ["福祉センター", "老人福祉センター", "障害者支援センター", "児童館"]
        }
        
        facility_name = random.choice(facility_names.get(use_type, ["施設"]))
        project_name = project_template.format(municipality + facility_name)
        
        # 日付を生成（今日から3ヶ月以内）
        bid_date = base_date + timedelta(days=random.randint(7, 90))
        notice_date = bid_date - timedelta(days=random.randint(14, 30))
        
        # 金額を生成（50百万〜5000百万円）
        estimated_price = random.randint(50, 5000) * 1000000
        minimum_price = int(estimated_price * random.uniform(0.7, 0.9))
        
        # 面積を生成（500〜20000㎡）
        floor_area = random.randint(500, 20000)
        
        sample_tenders.append((
            f"SAMPLE-{i+1:05d}",  # tender_id
            project_name,  # title
            f"{prefecture}{municipality}",  # publisher
            prefecture,  # prefecture
            municipality,  # municipality
            f"{prefecture}{municipality}1-2-3",  # address
            use_type,  # use_type
            bid_method,  # bid_method
            floor_area,  # floor_area_m2
            bid_date.date(),  # bid_date
            notice_date.date(),  # notice_date
            estimated_price,  # estimated_price
            minimum_price,  # minimum_price
            random.choice([True, False]),  # jv_allowed
            f"https://example.com/tender/{i+1}"  # origin_url
        ))
    
    # データベースに挿入
    insert_query = """
        INSERT INTO open_tenders (
            tender_id, title, publisher, prefecture, municipality,
            address, use_type, bid_method, floor_area_m2,
            bid_date, notice_date, estimated_price, minimum_price,
            jv_allowed, origin_url
        ) VALUES %s
        ON CONFLICT (tender_id) DO NOTHING
    """
    
    execute_values(cursor, insert_query, sample_tenders)
    conn.commit()
    
    print(f"Successfully inserted {len(sample_tenders)} sample tender records")
    
    # 確認のため件数を表示
    cursor.execute("SELECT COUNT(*) FROM open_tenders WHERE tender_id LIKE 'SAMPLE-%'")
    count = cursor.fetchone()[0]
    print(f"Total sample records in database: {count}")
    
    cursor.close()

def main():
    """メイン処理"""
    try:
        conn = get_db_connection()
        print("Connected to database successfully")
        
        populate_sample_tenders(conn)
        
        conn.close()
        print("Database population completed successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()