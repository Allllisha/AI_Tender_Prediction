#!/usr/bin/env python
"""
四国地方の入札データを追加するスクリプト
"""
import psycopg2
import os
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

# 環境変数の読み込み
if os.path.exists('.env'):
    load_dotenv()

def get_connection():
    """データベース接続を取得"""
    # Docker環境の接続情報
    return psycopg2.connect(
        host=os.getenv('DB_HOST', '127.0.0.1'),
        port=os.getenv('DB_PORT', 5434),
        database=os.getenv('DB_NAME', 'bid_kacho_db'),
        user=os.getenv('DB_USER', 'bid_user'),
        password=os.getenv('DB_PASSWORD', 'bid_password_2024')
    )

def add_shikoku_tenders():
    """四国地方の入札データを追加"""
    
    # 四国地方の都道府県と市区町村のマッピング
    shikoku_data = {
        '徳島県': ['徳島市', '鳴門市', '小松島市', '阿南市', '吉野川市', '阿波市', '美馬市', '三好市'],
        '香川県': ['高松市', '丸亀市', '坂出市', '善通寺市', '観音寺市', 'さぬき市', '東かがわ市', '三豊市'],
        '愛媛県': ['松山市', '今治市', '宇和島市', '八幡浜市', '新居浜市', '西条市', '大洲市', '伊予市', '四国中央市', '西予市', '東温市'],
        '高知県': ['高知市', '室戸市', '安芸市', '南国市', '土佐市', '須崎市', '宿毛市', '土佐清水市', '四万十市', '香南市', '香美市']
    }
    
    # 工事用途の種類
    use_types = ['学校', '庁舎', '公民館', '病院', '福祉施設', '道路', '橋梁', '公園', '上下水道', '住宅']
    
    # 調達方式
    methods = ['一般競争入札', '総合評価落札方式', '指名競争入札', '随意契約']
    
    # 発注者のパターン
    publisher_patterns = ['県', '市', '町', '村', '財団法人', '独立行政法人']
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 各県ごとにデータを生成
        total_count = 0
        for prefecture, cities in shikoku_data.items():
            # 各県に2000～3000件のデータを生成
            num_records = random.randint(2000, 3000)
            
            for i in range(num_records):
                # ランダムに市区町村を選択
                municipality = random.choice(cities)
                
                # 入札IDを生成（県コードを含む）
                prefecture_code = {
                    '徳島県': '36',
                    '香川県': '37',
                    '愛媛県': '38',
                    '高知県': '39'
                }[prefecture]
                
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
                
                # 発注者を生成
                publisher_suffix = random.choice(publisher_patterns)
                if publisher_suffix in ['県']:
                    publisher = f"{prefecture}"
                elif publisher_suffix in ['市', '町', '村']:
                    publisher = f"{municipality}"
                else:
                    publisher = f"{publisher_suffix}{municipality}"
                
                # 日付を生成（2024年1月～2025年12月）
                base_date = datetime(2024, 1, 1)
                random_days = random.randint(0, 730)
                bid_date = base_date + timedelta(days=random_days)
                notice_date = bid_date - timedelta(days=random.randint(14, 60))
                
                # 延床面積（100～10000㎡）
                floor_area = random.randint(100, 10000)
                
                # 予定価格（1000万～50億円）
                estimated_price = random.randint(10_000_000, 5_000_000_000)
                # 最低制限価格（予定価格の70～90%）
                min_price_ratio = random.uniform(0.7, 0.9)
                minimum_price = int(estimated_price * min_price_ratio)
                
                # JV可否
                jv_allowed = random.choice([True, False])
                if estimated_price > 1_000_000_000:
                    jv_allowed = True  # 10億円以上はJV可とする
                
                # 調達方式
                method = random.choice(methods)
                
                # 住所テキスト
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
                    'shikoku_mock',  # source
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
        
        # 最終的な確認
        cursor.execute("""
            SELECT prefecture, COUNT(*) as count 
            FROM tenders_open 
            WHERE prefecture IN ('徳島県', '香川県', '愛媛県', '高知県')
            GROUP BY prefecture
            ORDER BY prefecture
        """)
        
        print("\n📊 追加結果:")
        for row in cursor.fetchall():
            print(f"  {row[0]}: {row[1]} 件")
        
        print(f"\n✅ 合計 {total_count} 件の四国地方データを追加しました")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🔄 四国地方の入札データを追加中...")
    add_shikoku_tenders()