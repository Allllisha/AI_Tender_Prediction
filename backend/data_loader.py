import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse, unquote
import os
from dotenv import load_dotenv

# 環境変数を読み込み（ローカル開発時のみ）
# Docker/App Serviceでは環境変数が直接設定されるため不要
if os.path.exists('.env'):
    load_dotenv()

class DataLoader:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        print(f"DEBUG: DATABASE_URL from env: {self.db_url[:50] if self.db_url else 'NOT SET'}...")
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # Parse and create connection string
        parsed = urlparse(self.db_url)
        password = unquote(parsed.password) if parsed.password else None
        # Azure PostgreSQLはSSL必要、ローカルDockerは不要
        if 'localhost' in parsed.hostname or '127.0.0.1' in parsed.hostname:
            sslmode = 'disable'
        else:
            # URLにsslmodeパラメータがあれば使用、なければrequire
            import re
            sslmode = 'require'
            if '?' in self.db_url:
                params = self.db_url.split('?')[1]
                sslmode_match = re.search(r'sslmode=([^&]+)', params)
                if sslmode_match:
                    sslmode = sslmode_match.group(1)
        self.db_connection_str = f"host={parsed.hostname} port={parsed.port or 5432} dbname={parsed.path.lstrip('/')} user={parsed.username} password={password} sslmode={sslmode}"
        
        self.award_data = None
        self.company_data = None
        self.tender_data = None
        self._data_loaded = False
        
        # 起動時の接続を試みるが、失敗してもアプリケーションは起動する
        try:
            self.load_all_data()
            self._data_loaded = True
            print("DataLoader: Successfully loaded all data")
        except Exception as e:
            print(f"DataLoader: Failed to load data on startup: {e}")
            print("DataLoader: Will retry on first request")
            # 空のリストを設定
            self.award_data = []
            self.company_data = []
            self.tender_data = []
    
    def get_db_connection(self):
        """データベース接続を取得"""
        parsed = urlparse(self.db_url)
        
        # デバッグ情報を出力
        print(f"Connecting to: {parsed.hostname}")
        print(f"Database: {parsed.path.lstrip('/')}")
        print(f"User: {parsed.username}")
        # パスワードをデコードして接続
        from urllib.parse import unquote
        password = unquote(parsed.password) if parsed.password else None
        print(f"Password decoded: {'*' * len(password) if password else 'None'}")
        
        # URLパラメータからsslmodeを取得
        import re
        # デフォルトはrequire（Azure用）、URLにsslmodeが指定されていればそれを使用
        sslmode = 'require'
        if '?' in self.db_url:
            params = self.db_url.split('?')[1]
            sslmode_match = re.search(r'sslmode=([^&]+)', params)
            if sslmode_match:
                sslmode = sslmode_match.group(1)
        
        # ローカルDockerの場合はSSLを無効化
        if 'localhost' in parsed.hostname or '127.0.0.1' in parsed.hostname:
            sslmode = 'disable'
        
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip('/').split('?')[0],  # クエリパラメータを除外
            user=parsed.username,
            password=password,  # デコードしたパスワードを使用
            sslmode=sslmode,
            cursor_factory=RealDictCursor
        )
        return conn
    
    def load_all_data(self):
        """データベースからすべてのデータを読み込み"""
        conn = self.get_db_connection()
        
        try:
            # 市場全体の落札データを読み込み
            query_awards = """
                SELECT 
                    tender_id,
                    project_name,
                    contractor as publisher,
                    prefecture,
                    municipality,
                    prefecture || municipality as address,
                    use_type,
                    bid_method,
                    floor_area_m2,
                    contract_date as award_date,
                    contractor,
                    contract_amount,
                    estimated_price,
                    win_rate,
                    participants_count,
                    evaluation_score as technical_score,
                    contract_date
                FROM awards
                WHERE contractor != '星田建設株式会社' OR contractor IS NULL
            """
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query_awards)
            self.award_data = cursor.fetchall()
            cursor.close()
            
            # 自社の落札実績データを読み込み
            query_company = """
                SELECT 
                    tender_id,
                    project_name,
                    contractor as publisher,
                    prefecture,
                    municipality,
                    prefecture || municipality as address,
                    use_type,
                    bid_method,
                    floor_area_m2,
                    contract_date as award_date,
                    contractor,
                    contract_amount,
                    estimated_price,
                    win_rate,
                    participants_count,
                    evaluation_score,
                    contract_date
                FROM awards
                WHERE contractor = '星田建設株式会社'
            """
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query_company)
            self.company_data = cursor.fetchall()
            cursor.close()
            
            # 入札予定案件データを読み込み
            query_tenders = """
                SELECT 
                    tender_id,
                    title,
                    publisher,
                    prefecture,
                    municipality,
                    address_text,
                    use_type as use,
                    method,
                    floor_area_m2,
                    bid_date,
                    notice_date,
                    estimated_price_jpy,
                    minimum_price_jpy,
                    jv_allowed,
                    origin_url,
                    last_seen_at
                FROM tenders_open
                WHERE bid_date >= CURRENT_DATE
                AND tender_id NOT LIKE 'tender_id%'
                ORDER BY bid_date
            """
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query_tenders)
            self.tender_data = cursor.fetchall()
            cursor.close()
            
            # データ型の調整は不要（既にDBから正しい型で取得）
            
            print(f"Loaded {len(self.award_data)} award records from database")
            print(f"Loaded {len(self.company_data)} company records from database")
            print(f"Loaded {len(self.tender_data)} tender records from database")
            
        except Exception as e:
            print(f"Error loading data from database: {e}")
            # エラー時は空のリストを作成
            self.award_data = []
            self.company_data = []
            self.tender_data = []
            
        finally:
            conn.close()
    
    def ensure_data_loaded(self):
        """データが読み込まれていない場合は再試行"""
        if not self._data_loaded:
            try:
                print("Retrying data load...")
                self.load_all_data()
                self._data_loaded = True
                print("Data successfully loaded on retry")
            except Exception as e:
                print(f"Failed to load data on retry: {e}")
                raise
    
    def get_award_data(self):
        """市場全体の落札データを取得"""
        self.ensure_data_loaded()
        return self.award_data
    
    def get_company_award_data(self):
        """自社の落札実績データを取得"""
        return self.company_data
    
    def get_tender_data(self):
        """入札予定案件データを取得"""
        return self.tender_data
    
    def get_combined_award_data(self):
        """市場全体と自社の落札データを結合"""
        if not self.award_data and not self.company_data:
            return []
        elif not self.award_data:
            return self.company_data
        elif not self.company_data:
            return self.award_data
        else:
            # リストを結合
            return self.award_data + self.company_data
    
    def get_filter_options(self):
        """フィルタオプションを取得"""
        conn = psycopg2.connect(self.db_connection_str, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        try:
            # 都道府県リスト（最新1000件から取得）
            cursor.execute("SELECT DISTINCT prefecture FROM (SELECT prefecture FROM tenders_open WHERE prefecture IS NOT NULL ORDER BY bid_date DESC LIMIT 1000) t ORDER BY prefecture")
            prefectures = [row['prefecture'] for row in cursor.fetchall()]
            
            # 市区町村リスト（最新1000件から取得）
            cursor.execute("SELECT DISTINCT municipality FROM (SELECT municipality FROM tenders_open WHERE municipality IS NOT NULL ORDER BY bid_date DESC LIMIT 1000) t ORDER BY municipality")
            municipalities = [row['municipality'] for row in cursor.fetchall()]
            
            # 用途種別リスト（最新1000件から取得）
            cursor.execute("SELECT DISTINCT use_type FROM (SELECT use_type FROM tenders_open WHERE use_type IS NOT NULL ORDER BY bid_date DESC LIMIT 1000) t ORDER BY use_type")
            use_types = [row['use_type'] for row in cursor.fetchall()]
            
            # 入札方式リスト（最新1000件から取得）
            cursor.execute("SELECT DISTINCT method FROM (SELECT method FROM tenders_open WHERE method IS NOT NULL ORDER BY bid_date DESC LIMIT 1000) t ORDER BY method")
            bid_methods = [row['method'] for row in cursor.fetchall()]
            
            # 都道府県別の市区町村マッピング（最新1000件から取得）
            cursor.execute("""
                SELECT DISTINCT prefecture, municipality 
                FROM (SELECT prefecture, municipality FROM tenders_open 
                      WHERE prefecture IS NOT NULL AND municipality IS NOT NULL 
                      ORDER BY bid_date DESC LIMIT 1000) t
                ORDER BY prefecture, municipality
            """)
            prefecture_municipalities = {}
            for row in cursor.fetchall():
                pref = row['prefecture']
                muni = row['municipality']
                if pref not in prefecture_municipalities:
                    prefecture_municipalities[pref] = []
                prefecture_municipalities[pref].append(muni)
            
            return {
                'prefectures': prefectures,
                'municipalities': municipalities,
                'use_types': use_types,
                'bid_methods': bid_methods,
                'prefecture_municipalities': prefecture_municipalities
            }
            
        finally:
            cursor.close()
            conn.close()
    
    def search_tenders(self, filters=None):
        """条件に基づいて入札案件を検索"""
        try:
            conn = psycopg2.connect(self.db_connection_str, cursor_factory=RealDictCursor)
            
            # 基本クエリ
            query = """
                SELECT 
                    tender_id,
                    title,
                    publisher,
                    prefecture,
                    municipality,
                    address_text,
                    use_type,
                    method as bid_method,
                    floor_area_m2,
                    bid_date,
                    notice_date,
                    estimated_price_jpy as estimated_price,
                    minimum_price_jpy as minimum_price,
                    jv_allowed,
                    origin_url
                FROM tenders_open
                WHERE tender_id NOT LIKE %s
            """
            
            params = ['tender_id%']  # 最初のパラメータを追加
            
            if filters:
                print(f"DEBUG search_tenders: Received filters: {filters}")
                if filters.get('prefecture'):
                    query += " AND prefecture = %s"
                    params.append(filters['prefecture'])
                    print(f"DEBUG search_tenders: Added prefecture filter: {filters['prefecture']}")
                
                if filters.get('municipality'):
                    query += " AND municipality = %s"
                    params.append(filters['municipality'])
                
                if filters.get('use_type'):
                    query += " AND use_type = %s"
                    params.append(filters['use_type'])
                
                if filters.get('bid_method'):
                    query += " AND method = %s"
                    params.append(filters['bid_method'])
                
                if filters.get('min_floor_area'):
                    query += " AND floor_area_m2 >= %s"
                    params.append(filters['min_floor_area'])
                
                if filters.get('max_floor_area'):
                    query += " AND floor_area_m2 <= %s"
                    params.append(filters['max_floor_area'])
                
                if filters.get('min_price'):
                    query += " AND estimated_price >= %s"
                    params.append(filters['min_price'])
                
                if filters.get('max_price'):
                    query += " AND estimated_price <= %s"
                    params.append(filters['max_price'])
            
            query += " ORDER BY bid_date LIMIT 2000"
            
            print(f"DEBUG search_tenders: Final query: {query}")
            print(f"DEBUG search_tenders: Parameters: {params}")
            
            # カーソルを使って直接クエリを実行
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # 辞書のリストとして結果を取得
            results = cursor.fetchall()
            print(f"DEBUG search_tenders: Found {len(results)} results")
            cursor.close()
            conn.close()
            
            # 辞書のリストを返す
            return results
        except Exception as e:
            print(f"Error in search_tenders: {e}")
            import traceback
            traceback.print_exc()
            # エラー時は空のリストを返す
            return []
    
    def get_tender_by_id(self, tender_id: str):
        """特定のIDの案件を取得"""
        try:
            conn = psycopg2.connect(self.db_connection_str, cursor_factory=RealDictCursor)
            cursor = conn.cursor()
            
            query = """
                SELECT tender_id, source, publisher, title, prefecture, municipality, 
                       address_text, use_type, method as bid_method, jv_allowed, floor_area_m2, 
                       bid_date, notice_date, origin_url, estimated_price_jpy as estimated_price, 
                       minimum_price_jpy as minimum_price
                FROM tenders_open
                WHERE tender_id = %s
            """
            
            cursor.execute(query, (tender_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result:
                # 日付型を文字列に変換
                if result.get('bid_date'):
                    result['bid_date'] = result['bid_date'].strftime('%Y-%m-%d') if result['bid_date'] else ''
                if result.get('notice_date'):
                    result['notice_date'] = result['notice_date'].strftime('%Y-%m-%d') if result['notice_date'] else ''
            
            return dict(result) if result else None
            
        except Exception as e:
            print(f"Error in get_tender_by_id: {e}")
            return None
    
    def get_similar_awards(self, prefecture=None, use_type=None, floor_area=None, bid_method=None, estimated_price=None):
        """類似案件の落札実績を取得"""
        try:
            conn = psycopg2.connect(self.db_connection_str)
            cursor = conn.cursor()
            
            # 用途のマッピング（詳細な用途を汎用カテゴリに変換）
            use_type_mapping = {
                '下水道施設': '施設',  # インフラ系
                '福祉施設': '施設',
                '環境施設': '施設',
                '交通施設': '道路',    # 交通インフラ
                '観光施設': '施設',
                '公園施設': '施設',
                '文化施設': '公民館',  # 文化系
                '研究施設': '施設',
                '体育施設': '体育館',
                '公営住宅': '住宅',
                '市民センター': '公民館',
                '駐車場': '施設',
                '消防署': '庁舎',
                '警察署': '庁舎',
            }
            
            # マッピングを適用
            mapped_use_type = use_type_mapping.get(use_type, use_type) if use_type else None
            
            print(f"DEBUG get_similar_awards: Input params - prefecture={prefecture}, use_type={use_type}→{mapped_use_type}, floor_area={floor_area}, bid_method={bid_method}, estimated_price={estimated_price}")
            
            # まず全条件で検索（企業の多様性を確保）
            base_conditions = []
            params = []
            conditions_used = []
            
            # 条件を追加
            if prefecture:
                base_conditions.append("prefecture = %s")
                params.append(prefecture)
                conditions_used.append(f"prefecture={prefecture}")
            if use_type:
                base_conditions.append("use_type = %s")
                params.append(mapped_use_type if mapped_use_type else use_type)
                conditions_used.append(f"use_type={use_type}→{mapped_use_type if mapped_use_type else use_type}")
            if bid_method:
                base_conditions.append("bid_method = %s")
                params.append(bid_method)
                conditions_used.append(f"bid_method={bid_method}")
            if floor_area:
                # 面積の±30%範囲で検索
                base_conditions.append("floor_area_m2 BETWEEN %s AND %s")
                params.extend([float(floor_area) * 0.7, float(floor_area) * 1.3])
                conditions_used.append(f"floor_area={floor_area}±30%")
            if estimated_price:
                # 予定価格の±20%範囲で検索
                base_conditions.append("estimated_price BETWEEN %s AND %s")
                params.extend([float(estimated_price) * 0.8, float(estimated_price) * 1.2])
                conditions_used.append(f"estimated_price={estimated_price}±20%")
            
            # WHERE句を構築
            where_clause = " AND ".join(base_conditions) if base_conditions else "1=1"
            
            # 企業の多様性を確保するクエリ（星田建設を除外or制限）
            query = f"""
                WITH ranked_awards AS (
                    SELECT *,
                           ROW_NUMBER() OVER (PARTITION BY contractor ORDER BY contract_date DESC) as rn,
                           CASE WHEN contractor = '星田建設株式会社' THEN 1 ELSE 0 END as is_hoshida
                    FROM awards
                    WHERE {where_clause}
                )
                SELECT * FROM ranked_awards
                WHERE (is_hoshida = 0 AND rn <= 3) OR (is_hoshida = 1 AND rn <= 1)  -- 星田は1件、他は3件まで
                ORDER BY is_hoshida ASC, contract_date DESC  -- 星田以外を優先
                LIMIT 100
            """
            
            print(f"DEBUG get_similar_awards: Conditions used: {conditions_used}")
            print(f"DEBUG get_similar_awards: Query: {query}")
            print(f"DEBUG get_similar_awards: Params: {params}")
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            results = cursor.fetchall()
            
            # 結果が少ない場合は条件を緩和
            if len(results) < 5:
                print(f"DEBUG get_similar_awards: Only {len(results)} results found, relaxing conditions...")
                
                # STEP 1: 都道府県と用途の優先順位付きで価格範囲を広げる
                if estimated_price:
                    query = """
                        WITH ranked_awards AS (
                            SELECT *,
                                   CASE 
                                       WHEN prefecture = %s AND use_type = %s THEN 1  -- 完全一致
                                       WHEN prefecture = %s THEN 2                     -- 同じ都道府県優先
                                       WHEN use_type = %s THEN 3                       -- 同じ用途
                                       ELSE 4                                           -- その他
                                   END as priority,
                                   ABS(contract_amount - %s) as price_distance,
                                   ROW_NUMBER() OVER (PARTITION BY contractor ORDER BY 
                                       CASE 
                                           WHEN prefecture = %s AND use_type = %s THEN 1
                                           WHEN prefecture = %s THEN 2
                                           WHEN use_type = %s THEN 3
                                           ELSE 4
                                       END, ABS(contract_amount - %s)) as rn,
                                   CASE WHEN contractor = '星田建設株式会社' THEN 1 ELSE 0 END as is_hoshida
                            FROM awards
                            WHERE contract_amount BETWEEN %s AND %s
                        )
                        SELECT * FROM ranked_awards
                        WHERE (is_hoshida = 0 AND rn <= 3) OR (is_hoshida = 1 AND rn <= 1)  -- 星田は1件まで
                        ORDER BY is_hoshida ASC, priority, price_distance  -- 星田以外を優先
                        LIMIT 100
                    """
                    target_price = float(estimated_price) * 0.9
                    params = [
                        prefecture if prefecture else '', 
                        mapped_use_type if mapped_use_type else '',     # for CASE - 完全一致
                        prefecture if prefecture else '',  # for CASE - 県のみ
                        mapped_use_type if mapped_use_type else '',     # for CASE - 用途のみ
                        target_price,                      # for price_distance
                        # ROW_NUMBER用のパラメータ
                        prefecture if prefecture else '',
                        mapped_use_type if mapped_use_type else '',
                        prefecture if prefecture else '',
                        mapped_use_type if mapped_use_type else '',
                        target_price,                      # for ROW_NUMBER price distance
                        target_price * 0.5,                # price range min
                        target_price * 1.5                 # price range max
                    ]
                    
                    print(f"DEBUG get_similar_awards: Relaxed query with prefecture/use_type priority")
                    cursor.execute(query, params)
                    columns = [desc[0] for desc in cursor.description]
                    results = cursor.fetchall()
                
                # STEP 2: より広い価格帯で検索（±60%）
                if len(results) < 10 and estimated_price:
                    query = """
                        WITH ranked_awards AS (
                            SELECT *,
                                   CASE 
                                       WHEN prefecture = %s THEN 1    -- 同じ都道府県を最優先
                                       WHEN use_type = %s THEN 2      -- 同じ用途は次
                                       ELSE 3                          -- その他
                                   END as similarity_score,
                                   ABS(contract_amount - %s) as price_distance,
                                   ROW_NUMBER() OVER (PARTITION BY contractor ORDER BY ABS(contract_amount - %s)) as rn,
                                   CASE WHEN contractor = '星田建設株式会社' THEN 1 ELSE 0 END as is_hoshida
                            FROM awards
                            WHERE contract_amount BETWEEN %s AND %s
                        )
                        SELECT * FROM ranked_awards
                        WHERE (is_hoshida = 0 AND rn <= 2) OR (is_hoshida = 1 AND rn <= 1)  -- 星田は1件まで
                        ORDER BY is_hoshida ASC, similarity_score, price_distance
                        LIMIT 100
                    """
                    target_price = float(estimated_price) * 0.9
                    params = [
                        prefecture if prefecture else '',
                        mapped_use_type if mapped_use_type else '',
                        target_price,  # for price_distance
                        target_price,  # for ROW_NUMBER price distance
                        target_price * 0.4,  # より広い範囲（40%～160%）
                        target_price * 1.6,
                    ]
                    print(f"DEBUG get_similar_awards: Extended price range with prefecture priority ({target_price * 0.4/100000000:.1f}億～{target_price * 1.6/100000000:.1f}億)")
                    cursor.execute(query, params)
                    columns = [desc[0] for desc in cursor.description]
                    results = cursor.fetchall()
                    
                # 最終手段：全データから価格が近いもの（企業の多様性を確保）
                if len(results) < 5:
                    if estimated_price:
                        # 価格が近いものを取得しつつ、企業の多様性を確保
                        query = """
                            WITH ranked_awards AS (
                                SELECT *,
                                       ROW_NUMBER() OVER (PARTITION BY contractor ORDER BY ABS(contract_amount - %s)) as rn,
                                       ABS(contract_amount - %s) as price_distance
                                FROM awards
                                WHERE contract_amount BETWEEN %s AND %s
                            )
                            SELECT * FROM ranked_awards
                            WHERE (contractor != '星田建設株式会社' AND rn <= 2) OR (contractor = '星田建設株式会社' AND rn <= 1)  -- 星田は1件まで
                            ORDER BY price_distance
                            LIMIT 100
                        """
                        target_price = float(estimated_price) * 0.9
                        params = [
                            target_price,  # for price distance calculation
                            target_price,  # for price distance in SELECT
                            target_price * 0.3,  # 広い範囲（30%～170%）
                            target_price * 1.7
                        ]
                        print(f"DEBUG get_similar_awards: Using diverse contractor data with price proximity")
                        cursor.execute(query, params)
                    else:
                        # 予定価格がない場合は単純に多様性を確保
                        query = """
                            WITH ranked_awards AS (
                                SELECT *,
                                       ROW_NUMBER() OVER (PARTITION BY contractor ORDER BY contract_amount DESC) as rn
                                FROM awards
                            )
                            SELECT * FROM ranked_awards
                            WHERE (contractor != '星田建設株式会社' AND rn <= 2) OR (contractor = '星田建設株式会社' AND rn <= 1)  -- 星田は1件まで
                            ORDER BY contract_amount DESC
                            LIMIT 100
                        """
                        print(f"DEBUG get_similar_awards: Using diverse contractor data sorted by price")
                        cursor.execute(query)
                    columns = [desc[0] for desc in cursor.description]
                    results = cursor.fetchall()
            
            print(f"DEBUG get_similar_awards: Final result count: {len(results)}")
            cursor.close()
            conn.close()
            
            # 辞書のリストとして返す
            if results:
                return [dict(zip(columns, row)) for row in results]
            else:
                return []
                
        except Exception as e:
            print(f"Error in get_similar_awards: {e}")
            return []
    
    def get_company_strengths(self, company_name: str):
        """会社の強み情報を取得"""
        try:
            conn = psycopg2.connect(self.db_connection_str)
            cursor = conn.cursor()
            
            # 会社の落札実績を集計
            query = """
                SELECT 
                    COUNT(*) as total_awards,
                    AVG(contract_amount) as avg_amount,
                    MAX(contract_amount) as max_amount,
                    MIN(contract_amount) as min_amount
                FROM awards
                WHERE contractor = %s
            """
            
            cursor.execute(query, (company_name,))
            result = cursor.fetchone()
            
            if result and result[0] > 0:  # 落札実績がある場合
                # 都道府県別の実績を取得
                query_prefecture = """
                    SELECT a.prefecture, COUNT(*) as count
                    FROM awards a
                    WHERE a.contractor = %s AND a.prefecture IS NOT NULL
                    GROUP BY a.prefecture
                    ORDER BY count DESC
                    LIMIT 5
                """
                cursor.execute(query_prefecture, (company_name,))
                prefecture_results = cursor.fetchall()
                
                cursor.close()
                conn.close()
                
                return {
                    'company_name': company_name,
                    'total_awards': result[0],
                    'avg_amount': float(result[1]) if result[1] else 0,
                    'max_amount': float(result[2]) if result[2] else 0,
                    'min_amount': float(result[3]) if result[3] else 0,
                    'top_prefectures': {row[0]: row[1] for row in prefecture_results}
                }
            else:
                cursor.close()
                conn.close()
                
                # 実績がない場合のデフォルト値
                return {
                    'company_name': company_name,
                    'total_awards': 0,
                    'avg_amount': 0,
                    'max_amount': 0,
                    'min_amount': 0,
                    'top_prefectures': {}
                }
                
        except Exception as e:
            print(f"Error in get_company_strengths: {e}")
            return {
                'company_name': company_name,
                'total_awards': 0,
                'avg_amount': 0,
                'max_amount': 0,
                'min_amount': 0,
                'top_prefectures': {}
            }