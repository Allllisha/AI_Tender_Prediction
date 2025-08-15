-- 初期化SQL: ユーザー管理と会社別データ
-- Ver. 1.0 - マルチテナント対応

-- 1. 建設会社マスタテーブル
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    company_code VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 会社別落札実績テーブル
CREATE TABLE IF NOT EXISTS company_awards (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    tender_id VARCHAR(100),
    project_name VARCHAR(500),
    publisher VARCHAR(200),
    prefecture VARCHAR(50),
    municipality VARCHAR(100),
    address_text TEXT,
    use_type VARCHAR(100),
    method VARCHAR(100),
    floor_area_m2 DECIMAL(10, 2),
    award_date DATE,
    award_amount_jpy BIGINT,
    estimated_price_jpy BIGINT,
    win_rate DECIMAL(5, 2), -- 落札率
    participants_count INTEGER,
    technical_score DECIMAL(5, 2), -- 総合評価方式の技術点
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (company_id, tender_id)
);

-- 3. CSVアップロード履歴テーブル
CREATE TABLE IF NOT EXISTS csv_upload_history (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    file_name VARCHAR(255),
    record_count INTEGER,
    upload_status VARCHAR(50), -- 'processing', 'completed', 'failed'
    error_message TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- 4. ユーザーセッション管理テーブル
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (token)
);

-- 5. 初期データ投入（星田建設株式会社）
INSERT INTO companies (company_code, company_name, email, password_hash, is_active)
VALUES 
    ('HOSHIDA001', '星田建設株式会社', 'admin@hoshida-kensetsu.co.jp', 
     '$2b$12$LQz1F8V3jH9Gz8HRo9Mq2OWiZGr.CQ7Jh/HY3cHR1R5yQz9R.sT/q', true),
    ('DEMO001', 'デモ建設株式会社', 'demo@demo-kensetsu.co.jp',
     '$2b$12$LQz1F8V3jH9Gz8HRo9Mq2OWiZGr.CQ7Jh/HY3cHR1R5yQz9R.sT/q', true)
ON CONFLICT (company_code) DO NOTHING;

-- 星田建設の過去実績サンプルデータ
INSERT INTO company_awards (
    company_id, tender_id, project_name, publisher, prefecture, municipality,
    use_type, method, floor_area_m2, award_date, award_amount_jpy, 
    estimated_price_jpy, win_rate, participants_count, technical_score
)
SELECT 
    (SELECT id FROM companies WHERE company_code = 'HOSHIDA001'),
    'SAMPLE-' || LPAD(generate_series::text, 5, '0'),
    CASE (random()*4)::int
        WHEN 0 THEN '〇〇小学校改築工事'
        WHEN 1 THEN '△△中学校体育館新築工事'
        WHEN 2 THEN '□□市民センター改修工事'
        WHEN 3 THEN '◇◇図書館増築工事'
        ELSE '××庁舎耐震補強工事'
    END,
    CASE (random()*3)::int
        WHEN 0 THEN '東京都'
        WHEN 1 THEN '東京都教育委員会'
        ELSE municipalities.name || '市'
    END,
    prefectures.name,
    municipalities.name,
    CASE (random()*4)::int
        WHEN 0 THEN '学校'
        WHEN 1 THEN '庁舎'
        WHEN 2 THEN '文化施設'
        ELSE '体育施設'
    END,
    CASE (random()*2)::int
        WHEN 0 THEN '一般競争入札'
        ELSE '総合評価方式'
    END,
    (2000 + random() * 8000)::decimal(10,2),
    CURRENT_DATE - (random() * 730)::int,
    (100000000 + random() * 900000000)::bigint,
    (110000000 + random() * 1000000000)::bigint,
    85 + random() * 10,
    3 + (random() * 7)::int,
    CASE 
        WHEN (random()*2)::int = 1 THEN (70 + random() * 25)::decimal(5,2)
        ELSE NULL
    END
FROM generate_series(1, 200),
    (VALUES ('東京都'), ('神奈川県'), ('千葉県'), ('埼玉県')) AS prefectures(name),
    (VALUES ('千代田区'), ('中央区'), ('港区'), ('新宿区'), ('渋谷区'),
            ('横浜市'), ('川崎市'), ('千葉市'), ('さいたま市')) AS municipalities(name)
WHERE random() < 0.05  -- 約200件のデータを生成
ON CONFLICT (company_id, tender_id) DO NOTHING;

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_companies_email ON companies(email);
CREATE INDEX IF NOT EXISTS idx_awards_company_id ON company_awards(company_id);
CREATE INDEX IF NOT EXISTS idx_awards_award_date ON company_awards(award_date DESC);
CREATE INDEX IF NOT EXISTS idx_awards_prefecture ON company_awards(prefecture);
CREATE INDEX IF NOT EXISTS idx_awards_municipality ON company_awards(municipality);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(token);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);

-- トリガー関数: updated_atの自動更新
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- トリガーの設定
CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_awards_updated_at BEFORE UPDATE ON company_awards 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 権限設定
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bid_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bid_user;

-- コメント追加
COMMENT ON TABLE companies IS '建設会社マスタ - マルチテナント管理';
COMMENT ON TABLE company_awards IS '会社別落札実績データ';
COMMENT ON TABLE csv_upload_history IS 'CSVアップロード履歴管理';
COMMENT ON TABLE user_sessions IS 'ユーザーセッション管理';

COMMENT ON COLUMN companies.password_hash IS 'bcryptでハッシュ化されたパスワード (デフォルト: password123)';
COMMENT ON COLUMN company_awards.win_rate IS '落札率 = (落札額 / 予定価格) * 100';
COMMENT ON COLUMN company_awards.technical_score IS '総合評価方式での技術点（100点満点）';