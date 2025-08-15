#!/usr/bin/env python3
import json
import random
from datetime import datetime, timedelta
import hashlib

# Constants
TOTAL_RECORDS = 224560
OUTPUT_FILE = '/Users/anemoto/bid_kacho/data/raw/mock_tender_data_224560.json'

# Prefecture data
PREFECTURES = {
    '東京都': ['千代田区', '港区', '新宿区', '文京区', '台東区', '墨田区', '江東区', '品川区', '目黒区', '大田区', '世田谷区', '渋谷区', '中野区', '杉並区', '豊島区', '北区', '荒川区', '板橋区', '練馬区', '足立区', '葛飾区', '江戸川区'],
    '神奈川県': ['横浜市', '川崎市', '相模原市', '横須賀市', '平塚市', '鎌倉市', '藤沢市', '小田原市', '茅ヶ崎市', '逗子市', '三浦市', '秦野市', '厚木市', '大和市', '伊勢原市', '海老名市', '座間市', '南足柄市', '綾瀬市'],
    '千葉県': ['千葉市', '市川市', '船橋市', '館山市', '木更津市', '松戸市', '野田市', '茂原市', '成田市', '佐倉市', '東金市', '旭市', '習志野市', '柏市', '勝浦市', '市原市', '流山市', '八千代市', '我孫子市', '鴨川市', '鎌ケ谷市', '君津市', '富津市', '浦安市', '四街道市', '袖ケ浦市', '八街市', '印西市', '白井市', '富里市'],
    '埼玉県': ['さいたま市', '川越市', '熊谷市', '川口市', '行田市', '秩父市', '所沢市', '飯能市', '加須市', '本庄市', '東松山市', '春日部市', '狭山市', '羽生市', '鴻巣市', '深谷市', '上尾市', '草加市', '越谷市', '蕨市', '戸田市', '入間市', '朝霞市', '志木市', '和光市', '新座市', '桶川市', '久喜市', '北本市', '八潮市', '富士見市', '三郷市', '蓮田市', '坂戸市', '幸手市', '鶴ヶ島市', '日高市', '吉川市', 'ふじみ野市', '白岡市'],
    '大阪府': ['大阪市', '堺市', '岸和田市', '豊中市', '池田市', '吹田市', '泉大津市', '高槻市', '貝塚市', '守口市', '枚方市', '茨木市', '八尾市', '泉佐野市', '富田林市', '寝屋川市', '河内長野市', '松原市', '大東市', '和泉市', '箕面市', '柏原市', '羽曳野市', '門真市', '摂津市', '高石市', '藤井寺市', '東大阪市', '泉南市', '四條畷市', '交野市', '大阪狭山市', '阪南市'],
    '愛知県': ['名古屋市', '豊橋市', '岡崎市', '一宮市', '瀬戸市', '半田市', '春日井市', '豊川市', '津島市', '碧南市', '刈谷市', '豊田市', '安城市', '西尾市', '蒲郡市', '犬山市', '常滑市', '江南市', '小牧市', '稲沢市', '新城市', '東海市', '大府市', '知多市', '知立市', '尾張旭市', '高浜市', '岩倉市', '豊明市', '日進市', '田原市', '愛西市', '清須市', '北名古屋市', '弥富市', 'みよし市', 'あま市', '長久手市'],
    '福岡県': ['北九州市', '福岡市', '大牟田市', '久留米市', '直方市', '飯塚市', '田川市', '柳川市', '八女市', '筑後市', '大川市', '行橋市', '豊前市', '中間市', '小郡市', '筑紫野市', '春日市', '大野城市', '宗像市', '太宰府市', '古賀市', '福津市', '朝倉市', '糸島市', '那珂川市'],
    '北海道': ['札幌市', '函館市', '小樽市', '旭川市', '室蘭市', '釧路市', '帯広市', '北見市', '夕張市', '岩見沢市', '網走市', '留萌市', '苫小牧市', '稚内市', '美唄市', '芦別市', '江別市', '赤平市', '紋別市', '士別市', '名寄市', '三笠市', '根室市', '千歳市', '滝川市', '砂川市', '歌志内市', '深川市', '富良野市', '登別市', '恵庭市', '伊達市', '北広島市', '石狩市', '北斗市'],
    '宮城県': ['仙台市', '石巻市', '塩竈市', '気仙沼市', '白石市', '名取市', '角田市', '多賀城市', '岩沼市', '登米市', '栗原市', '東松島市', '大崎市'],
    '広島県': ['広島市', '呉市', '竹原市', '三原市', '尾道市', '福山市', '府中市', '三次市', '庄原市', '大竹市', '東広島市', '廿日市市', '安芸高田市', '江田島市'],
    '静岡県': ['静岡市', '浜松市', '沼津市', '熱海市', '三島市', '富士宮市', '伊東市', '島田市', '富士市', '磐田市', '焼津市', '掛川市', '藤枝市', '御殿場市', '袋井市', '下田市', '裾野市', '湖西市', '伊豆市', '御前崎市', '菊川市', '伊豆の国市', '牧之原市'],
    '京都府': ['京都市', '福知山市', '舞鶴市', '綾部市', '宇治市', '宮津市', '亀岡市', '城陽市', '向日市', '長岡京市', '八幡市', '京田辺市', '京丹後市', '南丹市', '木津川市'],
    '兵庫県': ['神戸市', '姫路市', '尼崎市', '明石市', '西宮市', '洲本市', '芦屋市', '伊丹市', '相生市', '豊岡市', '加古川市', '赤穂市', '西脇市', '宝塚市', '三木市', '高砂市', '川西市', '小野市', '三田市', '加西市', '丹波篠山市', '養父市', '丹波市', '南あわじ市', '朝来市', '淡路市', '宍粟市', '加東市', 'たつの市'],
    '新潟県': ['新潟市', '長岡市', '三条市', '柏崎市', '新発田市', '小千谷市', '加茂市', '十日町市', '見附市', '村上市', '燕市', '糸魚川市', '妙高市', '五泉市', '上越市', '阿賀野市', '佐渡市', '魚沼市', '南魚沼市', '胎内市'],
    '長野県': ['長野市', '松本市', '上田市', '岡谷市', '飯田市', '諏訪市', '須坂市', '小諸市', '伊那市', '駒ヶ根市', '中野市', '大町市', '飯山市', '茅野市', '塩尻市', '佐久市', '千曲市', '東御市', '安曇野市'],
    '岐阜県': ['岐阜市', '大垣市', '高山市', '多治見市', '関市', '中津川市', '美濃市', '瑞浪市', '羽島市', '恵那市', '美濃加茂市', '土岐市', '各務原市', '可児市', '山県市', '瑞穂市', '飛騨市', '本巣市', '郡上市', '下呂市', '海津市'],
    '栃木県': ['宇都宮市', '足利市', '栃木市', '佐野市', '鹿沼市', '日光市', '小山市', '真岡市', '大田原市', '矢板市', '那須塩原市', 'さくら市', '那須烏山市', '下野市'],
    '群馬県': ['前橋市', '高崎市', '桐生市', '伊勢崎市', '太田市', '沼田市', '館林市', '渋川市', '藤岡市', '富岡市', '安中市', 'みどり市'],
    '茨城県': ['水戸市', '日立市', '土浦市', '古河市', '石岡市', '結城市', '龍ケ崎市', '下妻市', '常総市', '常陸太田市', '高萩市', '北茨城市', '笠間市', '取手市', '牛久市', 'つくば市', 'ひたちなか市', '鹿嶋市', '潮来市', '守谷市', '常陸大宮市', '那珂市', '筑西市', '坂東市', '稲敷市', 'かすみがうら市', '桜川市', '神栖市', '行方市', '鉾田市', 'つくばみらい市', '小美玉市'],
    '山梨県': ['甲府市', '富士吉田市', '都留市', '山梨市', '大月市', '韮崎市', '南アルプス市', '北杜市', '甲斐市', '笛吹市', '上野原市', '甲州市', '中央市'],
    '岡山県': ['岡山市', '倉敷市', '津山市', '玉野市', '笠岡市', '井原市', '総社市', '高梁市', '新見市', '備前市', '瀬戸内市', '赤磐市', '真庭市', '美作市', '浅口市'],
}

# Building use types
USE_TYPES = [
    '学校', '庁舎', '文化施設', '体育施設', '病院', '公営住宅', 
    '福祉施設', '図書館', '公民館', '保育園', '消防署', '警察署',
    '市民センター', '研究施設', '環境施設', '観光施設', '駐車場',
    '公園施設', '交通施設', '下水道施設'
]

# Procurement methods
METHODS = ['一般競争入札', '総合評価方式', '指名競争入札', '随意契約', '公募型指名競争入札', '簡易公募型競争入札']

# Publishers
PUBLISHER_PATTERNS = [
    '{}', '{}市', '{}町', '{}村', '{}市役所', '{}町役場', '{}村役場',
    '{}県', '{}県庁', '{}府', '{}府庁', '国土交通省{}地方整備局',
    '{}市教育委員会', '{}県教育委員会', '{}市水道局', '{}県警察本部',
    '{}市消防局', '{}県立病院機構', '{}市立病院', '独立行政法人{}',
    '{}港湾局', '{}市交通局', '{}県道路公社', '{}市住宅供給公社'
]

# Project name patterns
PROJECT_NAME_PATTERNS = [
    '{}新築工事',
    '{}改修工事',
    '{}耐震補強工事',
    '{}増築工事',
    '{}解体工事',
    '{}大規模改修工事',
    '{}空調設備改修工事',
    '{}外壁改修工事',
    '{}屋上防水改修工事',
    '{}エレベーター設置工事',
    '{}バリアフリー化工事',
    '{}トイレ改修工事',
    '{}給排水設備改修工事',
    '{}電気設備改修工事',
    '{}建替工事',
    '{}リニューアル工事',
    '{}環境整備工事',
    '{}外構整備工事',
    '{}駐車場整備工事',
    '{}グラウンド改修工事'
]

def generate_tender_id(index, date):
    """Generate a unique tender ID"""
    date_str = date.strftime('%Y%m%d')
    hash_str = hashlib.md5(f"{index}{date_str}".encode()).hexdigest()[:6]
    return f"KKJ-{date_str}-{hash_str.upper()}"

def generate_tender_title(prefecture, municipality, use_type):
    """Generate a realistic tender title"""
    # Location-specific names
    location_names = {
        '学校': ['第一', '第二', '第三', '中央', '東', '西', '南', '北', '緑', '桜', '富士', '青葉', '若葉', '向陽', '朝日'],
        '庁舎': ['本', '新', '第二', '北', '南', '東', '西', '中央'],
        '文化施設': ['市民', '文化', '総合', '中央', '地域', 'コミュニティ'],
        '体育施設': ['総合', '市民', '中央', '東', '西', '南', '北', 'スポーツ'],
        '病院': ['総合', '中央', '市民', '地域医療', '救急医療'],
        '公営住宅': ['市営', '県営', '公営', '緑ヶ丘', '桜ヶ丘', '青葉', '若葉', '中央'],
        '福祉施設': ['総合', '地域', '高齢者', '障害者', '児童'],
        '図書館': ['中央', '市立', '県立', '地域', '子ども'],
        '公民館': ['中央', '地区', '市民', 'コミュニティ'],
        '保育園': ['中央', '第一', '第二', 'ひまわり', 'さくら', 'つくし', 'わかば']
    }
    
    name_prefix = random.choice(location_names.get(use_type, ['中央', '市民', '総合']))
    
    if use_type == '学校':
        school_type = random.choice(['小学校', '中学校', '高等学校'])
        facility_name = f"{municipality}{name_prefix}{school_type}"
    elif use_type == '病院':
        facility_name = f"{municipality}{name_prefix}病院"
    elif use_type == '庁舎':
        facility_name = f"{municipality}{name_prefix}庁舎"
    elif use_type == '文化施設':
        facility_type = random.choice(['文化会館', 'ホール', '文化センター', '市民会館'])
        facility_name = f"{municipality}{name_prefix}{facility_type}"
    elif use_type == '体育施設':
        facility_type = random.choice(['体育館', 'スポーツセンター', '運動公園', 'アリーナ'])
        facility_name = f"{municipality}{name_prefix}{facility_type}"
    elif use_type == '公営住宅':
        facility_name = f"{name_prefix}団地"
    elif use_type == '福祉施設':
        facility_type = random.choice(['福祉センター', '福祉会館', 'ケアセンター'])
        facility_name = f"{municipality}{name_prefix}{facility_type}"
    elif use_type == '図書館':
        facility_name = f"{municipality}{name_prefix}図書館"
    elif use_type == '公民館':
        facility_name = f"{municipality}{name_prefix}公民館"
    elif use_type == '保育園':
        facility_name = f"{municipality}{name_prefix}保育園"
    else:
        facility_name = f"{municipality}{use_type}"
    
    project_pattern = random.choice(PROJECT_NAME_PATTERNS)
    return project_pattern.format(facility_name)

def generate_floor_area():
    """Generate realistic floor area based on distribution"""
    # Weighted distribution
    weights = [
        (500, 2000, 0.3),    # Small projects: 30%
        (2000, 5000, 0.25),   # Medium-small: 25%
        (5000, 10000, 0.20),  # Medium: 20%
        (10000, 20000, 0.15), # Medium-large: 15%
        (20000, 50000, 0.08), # Large: 8%
        (50000, 100000, 0.02) # Very large: 2%
    ]
    
    rand = random.random()
    cumulative = 0
    for min_area, max_area, weight in weights:
        cumulative += weight
        if rand <= cumulative:
            return round(random.uniform(min_area, max_area), 1)
    
    return round(random.uniform(500, 2000), 1)  # Default to small

def generate_price(floor_area, use_type):
    """Generate estimated price based on floor area and use type"""
    # Base price per m2 (in JPY)
    base_prices = {
        '学校': 280000,
        '庁舎': 320000,
        '文化施設': 350000,
        '体育施設': 300000,
        '病院': 450000,
        '公営住宅': 220000,
        '福祉施設': 260000,
        '図書館': 310000,
        '公民館': 250000,
        '保育園': 240000,
        '消防署': 340000,
        '警察署': 360000,
        '市民センター': 270000,
        '研究施設': 380000,
        '環境施設': 290000,
        '観光施設': 330000,
        '駐車場': 150000,
        '公園施設': 180000,
        '交通施設': 400000,
        '下水道施設': 350000
    }
    
    base_price = base_prices.get(use_type, 250000)
    # Add some variation (±20%)
    price_per_m2 = base_price * random.uniform(0.8, 1.2)
    
    estimated_price = int(floor_area * price_per_m2)
    
    # Round to nearest million for large projects
    if estimated_price > 100000000:
        estimated_price = round(estimated_price / 1000000) * 1000000
    elif estimated_price > 10000000:
        estimated_price = round(estimated_price / 100000) * 100000
    else:
        estimated_price = round(estimated_price / 10000) * 10000
    
    return estimated_price

def generate_dates():
    """Generate bid date and notice date"""
    today = datetime.now()
    # Bid date: from 1 month ago to 4 months in the future
    start_date = today - timedelta(days=30)
    end_date = today + timedelta(days=120)
    
    bid_date = start_date + timedelta(days=random.randint(0, 150))
    
    # Notice date: 2-4 weeks before bid date
    notice_days_before = random.randint(14, 28)
    notice_date = bid_date - timedelta(days=notice_days_before)
    
    return bid_date, notice_date

def generate_single_tender(index):
    """Generate a single tender record"""
    # Select random location
    prefecture = random.choice(list(PREFECTURES.keys()))
    municipality = random.choice(PREFECTURES[prefecture])
    
    # Select use type and method
    use_type = random.choice(USE_TYPES)
    method = random.choice(METHODS)
    
    # Generate dates
    bid_date, notice_date = generate_dates()
    
    # Generate other attributes
    floor_area = generate_floor_area()
    estimated_price = generate_price(floor_area, use_type)
    
    # Generate minimum price (70-85% of estimated price)
    min_price_ratio = random.uniform(0.70, 0.85)
    minimum_price = int(estimated_price * min_price_ratio)
    
    # Generate publisher
    publisher_pattern = random.choice(PUBLISHER_PATTERNS)
    if '市' in municipality or '区' in municipality:
        publisher = publisher_pattern.format(municipality)
    else:
        publisher = publisher_pattern.format(prefecture)
    
    # JV allowed (more likely for large projects)
    jv_allowed = random.random() < 0.3 if floor_area > 10000 else random.random() < 0.1
    
    tender = {
        'tender_id': generate_tender_id(index, bid_date),
        'source': 'KKJ',
        'publisher': publisher,
        'title': generate_tender_title(prefecture, municipality, use_type),
        'prefecture': prefecture,
        'municipality': municipality,
        'address_text': f"{prefecture}{municipality}",
        'use': use_type,
        'method': method,
        'jv_allowed': jv_allowed,
        'floor_area_m2': floor_area,
        'bid_date': bid_date.strftime('%Y-%m-%d'),
        'notice_date': notice_date.strftime('%Y-%m-%d'),
        'estimated_price_jpy': estimated_price,
        'minimum_price_jpy': minimum_price,
        'origin_url': f"https://www.kkj.go.jp/tenders/{generate_tender_id(index, bid_date)}",
        'last_seen_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    return tender

def main():
    """Main function to generate all tender data"""
    print(f"Generating {TOTAL_RECORDS:,} tender records...")
    
    tenders = []
    
    # Generate records with progress updates
    for i in range(TOTAL_RECORDS):
        if i % 10000 == 0:
            print(f"Progress: {i:,}/{TOTAL_RECORDS:,} ({i*100/TOTAL_RECORDS:.1f}%)")
        
        tender = generate_single_tender(i)
        tenders.append(tender)
    
    # Sort by bid_date (most recent first)
    tenders.sort(key=lambda x: x['bid_date'], reverse=True)
    
    # Save to JSON file
    print(f"Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(tenders, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully generated {TOTAL_RECORDS:,} tender records!")
    
    # Print some statistics
    bid_dates = [datetime.strptime(t['bid_date'], '%Y-%m-%d') for t in tenders]
    min_date = min(bid_dates)
    max_date = max(bid_dates)
    
    print(f"\nStatistics:")
    print(f"  Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
    print(f"  Total prefectures: {len(set(t['prefecture'] for t in tenders))}")
    print(f"  Total use types: {len(set(t['use'] for t in tenders))}")
    print(f"  Average floor area: {sum(t['floor_area_m2'] for t in tenders) / len(tenders):.1f} m²")
    print(f"  Average estimated price: ¥{sum(t['estimated_price_jpy'] for t in tenders) / len(tenders):,.0f}")

if __name__ == "__main__":
    main()