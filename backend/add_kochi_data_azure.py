#!/usr/bin/env python
"""
Azure PostgreSQLに高知県の入札データを追加するスクリプト
"""
import psycopg2
import os
from datetime import datetime, timedelta
import random

def get_azure_connection():
    """Azure PostgreSQLへの接続を取得"""
    return psycopg2.connect(
        host='postgres-bid-kacho.postgres.database.azure.com',
        port=5432,
        database='bid_kacho_db',
        user='dbadmin',
        password='Password2024',
        sslmode='require'
    )

def add_kochi_tenders():
    """高知県の入札データを追加"""
    
    # 高知県の市区町村
    cities = ['高知市', '室戸市', '安芸市', '南国市', '土佐市', '須崎市', '宿毛市', '土佐清水市', '四万十市', '香南市', '香美市']
    
    # 工事用途の種類
    use_types = ['学校', '庁舎', '公民館', '病院', '福祉施設', '道路', '橋梁', '公園', '上下水道', '住宅']
    
    # 調達方式
    methods = ['一般競争入札', '総合評価落札方式', '指名競争入札', '随意契約']
    
    print("🔄 Azure PostgreSQLに接続中...")
    conn = get_azure_connection()
    cursor = conn.cursor()
    
    try:
        # 高知県に2500件のデータを生成
        num_records = 2500
        prefecture = '高知県'
        prefecture_code = '39'
        total_count = 0
        
        for i in range(num_records):
            municipality = random.choice(cities)
            tender_id = f"shikoku-{prefecture_code}-2024-{str(i+1).zfill(5)}"
            
            # 工事名を生成
            use_type = random.choice(use_types)
            facility_names = {
                '学校': ['小学校', '中学校', '高等学校'],
                '庁舎': ['市役所', '町役場', '県庁舎'],
                '公民館': ['公民館', 'コミュニティセンター', '交流センター'],
                '病院': ['総合病院', '市民病院', '診療所'],
                '福祉施設': ['老人ホーム', '介護施設', '児童館'],
                '道路': ['国道', '県道', '市道'],
                '橋梁': ['橋', '高架橋', '歩道橋'],
                '公園': ['総合公園', '運動公園', '児童公園'],
                '上下水道': ['配水管', '下水処理場', 'ポンプ場'],
                '住宅': ['市営住宅', '県営住宅', '公営住宅']
            }
            
            facility = random.choice(facility_names.get(use_type, ['施設']))
            work_type = random.choice(['新築', '改修', '耐震補強', '増築', '解体', '設備更新'])
            title = f"{municipality}{facility}{work_type}工事"
            
            # 発注者
            publisher_suffix = random.choice(['県', '市'])
            publisher = f"{prefecture}" if publisher_suffix == '県' else f"{municipality}"
            
            # 日付を生成
            base_date = datetime(2024, 1, 1)
            random_days = random.randint(0, 730)
            bid_date = base_date + timedelta(days=random_days)
            notice_date = bid_date - timedelta(days=random.randint(14, 60))
            
            # その他のパラメータ
            floor_area = random.randint(100, 10000)
            estimated_price = random.randint(10_000_000, 5_000_000_000)
            minimum_price = int(estimated_price * random.uniform(0.7, 0.9))
            jv_allowed = estimated_price > 1_000_000_000
            method = random.choice(methods)
            address_text = f"{prefecture}{municipality}"
            
            # SQLクエリ
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
            
            cursor.execute(insert_query, (
                tender_id,
                'shikoku_mock',
                publisher,
                title,
                prefecture,
                municipality,
                address_text,
                use_type,
                method,
                jv_allowed,
                floor_area,
                bid_date.strftime('%Y-%m-%d'),
                notice_date.strftime('%Y-%m-%d'),
                estimated_price,
                minimum_price,
                f"https://example.com/tenders/{tender_id}",
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))
            
            total_count += 1
            
            if (i + 1) % 500 == 0:
                print(f"  {prefecture}: {i + 1}/{num_records} 件を追加...")
                conn.commit()
        
        conn.commit()
        print(f"✅ {prefecture}: {num_records} 件のデータを追加完了")
        
        # 確認
        cursor.execute("""
            SELECT prefecture, COUNT(*) as count 
            FROM tenders_open 
            WHERE prefecture IN ('徳島県', '香川県', '愛媛県', '高知県')
            GROUP BY prefecture
            ORDER BY prefecture
        """)
        
        print("\n📊 四国地方のデータ:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} 件")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔄 高知県の入札データを追加中...")
    add_kochi_tenders()