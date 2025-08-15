# 入札インテリジェンスシステム - アーキテクチャ設計

## データ分離戦略

### 1. 入札情報（リアルタイム）
**データソース**: KKJ API  
**用途**: 現在公開中の入札案件の検索・表示
```
- 案件名、発注機関、公告日、入札日
- 予定価格、工事概要、参加条件
- リアルタイムで最新情報を取得
```

### 2. 落札情報（過去データ）
**データソース**: 各種サイトからクローリング（段階的に拡充）
**用途**: 類似案件の分析・予測モデルの学習データ
```
- 過去の落札金額、落札率
- 参加企業数、落札企業
- 地域・規模・用途別の統計データ
```

## システム構成

```python
# フロー図
[ユーザー] 
    ↓
[案件検索] → KKJ API（入札情報）
    ↓
[勝率予測] → 落札DBから類似案件を抽出
    ↓
[予測結果] → 類似案件の落札データに基づく分析
```

## 実装アプローチ

### Phase 1: MVP
1. **入札情報**: KKJ APIから取得
2. **落札情報**: サンプルデータまたは限定的なクローリング
3. **予測**: シンプルな統計的手法（中央値、分散）

### Phase 2: 拡張
1. **落札データ収集の自動化**
   - 主要自治体サイトのクローラー実装
   - データクレンジング・正規化処理

2. **予測精度向上**
   - 機械学習モデルの導入
   - 特徴量エンジニアリング

## メリット

1. **開発速度**: 入札情報はAPIで即座に取得可能
2. **柔軟性**: 落札データソースを段階的に追加可能
3. **精度向上**: 多様なデータソースから学習データを蓄積
4. **コスト効率**: 無料のAPIとクローリングで初期コストを抑制

## 技術スタック

```yaml
データ収集:
  入札情報: KKJ API (REST)
  落札情報: Selenium/BeautifulSoup (クローリング)

データ保存:
  PostgreSQL: 構造化データ
  Blob Storage: 生データアーカイブ

予測エンジン:
  初期: pandas + scipy (統計分析)
  将来: scikit-learn/LightGBM (機械学習)

API:
  FastAPI: REST API
  Redis: キャッシュ層
```

## データモデル例

```sql
-- 入札案件（KKJ APIから）
CREATE TABLE tenders_open (
    tender_id VARCHAR PRIMARY KEY,
    title TEXT,
    publisher TEXT,
    prefecture_code VARCHAR,
    floor_area_m2 NUMERIC,
    bid_date DATE,
    estimated_price_jpy BIGINT
);

-- 落札結果（クローリングで収集）
CREATE TABLE awards (
    award_id VARCHAR PRIMARY KEY,
    tender_title TEXT,  -- 案件名で類似性を判定
    awardee_name TEXT,
    award_amount_jpy BIGINT,
    award_date DATE,
    prefecture_code VARCHAR,
    floor_area_m2 NUMERIC
);

-- 類似案件の検索
-- tender_titleの類似性、prefecture_code、floor_area_m2の範囲で
-- 過去の落札データから類似案件を抽出
```

## 予測ロジック

```python
def predict_win_probability(tender_info, bid_amount):
    """
    入札案件情報と入札予定額から勝率を予測
    """
    # 1. 類似案件を落札DBから検索
    similar_awards = find_similar_awards(
        prefecture=tender_info.prefecture_code,
        floor_area_range=(tender_info.floor_area_m2 * 0.8, 
                         tender_info.floor_area_m2 * 1.2),
        limit=50
    )
    
    # 2. 統計分析
    median_price = calculate_median_price(similar_awards)
    price_variance = calculate_variance(similar_awards)
    
    # 3. 勝率計算
    win_prob = estimate_probability(
        bid_amount=bid_amount,
        median=median_price,
        variance=price_variance
    )
    
    return {
        'win_probability': win_prob,
        'confidence': len(similar_awards) / 50,  # データ量に基づく信頼度
        'basis': {
            'similar_cases': len(similar_awards),
            'median_price': median_price
        }
    }
```

この設計により、入札情報の即時性と落札データの分析力を両立できます。