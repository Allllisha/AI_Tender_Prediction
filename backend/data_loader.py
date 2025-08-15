import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
import os
from dotenv import load_dotenv

# 環境変数を読み込み
load_dotenv()

class DataLoader:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        self.award_data = None
        self.company_data = None
        self.tender_data = None
        self.load_all_data()
    
    def get_db_connection(self):
        """データベース接続を取得"""
        parsed = urlparse(self.db_url)
        
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password,
            sslmode='require',
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
                    publisher,
                    prefecture,
                    municipality,
                    address,
                    use_type,
                    method,
                    floor_area_m2,
                    award_date,
                    contractor,
                    award_amount_jpy as contract_amount,
                    estimated_price_jpy as estimated_price,
                    win_rate,
                    participants_count,
                    technical_score,
                    award_date as contract_date
                FROM awards
                WHERE contractor != '星田建設株式会社' OR contractor IS NULL
            """
            self.award_data = pd.read_sql(query_awards, conn)
            
            # 自社の落札実績データを読み込み
            query_company = """
                SELECT 
                    tender_id,
                    project_name,
                    publisher,
                    prefecture,
                    municipality,
                    address,
                    use_type,
                    method as bid_method,
                    floor_area_m2,
                    award_date,
                    contractor,
                    award_amount_jpy as contract_amount,
                    estimated_price_jpy as estimated_price,
                    win_rate,
                    participants_count,
                    technical_score as evaluation_score,
                    award_date as contract_date
                FROM awards
                WHERE contractor = '星田建設株式会社'
            """
            self.company_data = pd.read_sql(query_company, conn)
            
            # 入札予定案件データを読み込み
            query_tenders = """
                SELECT 
                    tender_id,
                    title,
                    publisher,
                    prefecture,
                    municipality,
                    address as address_text,
                    use_type as use,
                    bid_method as method,
                    floor_area_m2,
                    bid_date,
                    notice_date,
                    estimated_price as estimated_price_jpy,
                    minimum_price as minimum_price_jpy,
                    jv_allowed,
                    origin_url,
                    created_at as last_seen_at
                FROM open_tenders
                WHERE bid_date >= CURRENT_DATE
                ORDER BY bid_date
                LIMIT 10000
            """
            self.tender_data = pd.read_sql(query_tenders, conn)
            
            # データ型の調整
            if not self.award_data.empty:
                self.award_data['award_date'] = pd.to_datetime(self.award_data['award_date'], errors='coerce')
                self.award_data['contract_date'] = self.award_data['award_date']
            
            if not self.company_data.empty:
                self.company_data['award_date'] = pd.to_datetime(self.company_data['award_date'], errors='coerce')
                self.company_data['contract_date'] = self.company_data['award_date']
            
            if not self.tender_data.empty:
                self.tender_data['bid_date'] = pd.to_datetime(self.tender_data['bid_date'], errors='coerce')
                self.tender_data['notice_date'] = pd.to_datetime(self.tender_data['notice_date'], errors='coerce')
            
            print(f"Loaded {len(self.award_data)} award records from database")
            print(f"Loaded {len(self.company_data)} company records from database")
            print(f"Loaded {len(self.tender_data)} tender records from database")
            
        except Exception as e:
            print(f"Error loading data from database: {e}")
            # エラー時は空のDataFrameを作成
            self.award_data = pd.DataFrame()
            self.company_data = pd.DataFrame()
            self.tender_data = pd.DataFrame()
            
        finally:
            conn.close()
    
    def get_award_data(self):
        """市場全体の落札データを取得"""
        return self.award_data
    
    def get_company_award_data(self):
        """自社の落札実績データを取得"""
        return self.company_data
    
    def get_tender_data(self):
        """入札予定案件データを取得"""
        return self.tender_data
    
    def get_combined_award_data(self):
        """市場全体と自社の落札データを結合"""
        if self.award_data.empty and self.company_data.empty:
            return pd.DataFrame()
        elif self.award_data.empty:
            return self.company_data
        elif self.company_data.empty:
            return self.award_data
        else:
            # カラム名を統一
            company_data_copy = self.company_data.copy()
            if 'bid_method' in company_data_copy.columns:
                company_data_copy['method'] = company_data_copy['bid_method']
            if 'evaluation_score' in company_data_copy.columns:
                company_data_copy['technical_score'] = company_data_copy['evaluation_score']
            
            # 共通カラムのみを選択
            common_columns = list(set(self.award_data.columns) & set(company_data_copy.columns))
            
            return pd.concat([
                self.award_data[common_columns],
                company_data_copy[common_columns]
            ], ignore_index=True)
    
    def get_filter_options(self):
        """フィルタオプションを取得"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 都道府県リスト
            cursor.execute("SELECT DISTINCT prefecture FROM open_tenders WHERE prefecture IS NOT NULL ORDER BY prefecture")
            prefectures = [row['prefecture'] for row in cursor.fetchall()]
            
            # 市区町村リスト
            cursor.execute("SELECT DISTINCT municipality FROM open_tenders WHERE municipality IS NOT NULL ORDER BY municipality")
            municipalities = [row['municipality'] for row in cursor.fetchall()]
            
            # 用途種別リスト
            cursor.execute("SELECT DISTINCT use_type FROM open_tenders WHERE use_type IS NOT NULL ORDER BY use_type")
            use_types = [row['use_type'] for row in cursor.fetchall()]
            
            # 都道府県別の市区町村マッピング
            cursor.execute("""
                SELECT DISTINCT prefecture, municipality 
                FROM open_tenders 
                WHERE prefecture IS NOT NULL AND municipality IS NOT NULL 
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
                'prefecture_municipalities': prefecture_municipalities
            }
            
        finally:
            cursor.close()
            conn.close()
    
    def search_tenders(self, filters=None):
        """条件に基づいて入札案件を検索"""
        conn = self.get_db_connection()
        
        # 基本クエリ
        query = """
            SELECT 
                tender_id,
                title,
                publisher,
                prefecture,
                municipality,
                address as address_text,
                use_type,
                bid_method,
                floor_area_m2,
                bid_date,
                notice_date,
                estimated_price,
                minimum_price,
                jv_allowed,
                origin_url
            FROM open_tenders
            WHERE bid_date >= CURRENT_DATE
        """
        
        params = []
        
        if filters:
            if filters.get('prefecture'):
                query += " AND prefecture = %s"
                params.append(filters['prefecture'])
            
            if filters.get('municipality'):
                query += " AND municipality = %s"
                params.append(filters['municipality'])
            
            if filters.get('use_type'):
                query += " AND use_type = %s"
                params.append(filters['use_type'])
            
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
        
        query += " ORDER BY bid_date LIMIT 1000"
        
        result_df = pd.read_sql(query, conn, params=params or None)
        conn.close()
        
        # データ型の調整
        if not result_df.empty:
            result_df['bid_date'] = pd.to_datetime(result_df['bid_date'], errors='coerce')
            result_df['notice_date'] = pd.to_datetime(result_df['notice_date'], errors='coerce')
        
        return result_df