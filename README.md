# 建築入札インテリジェンス・システム

## 概要
ゼネコンの営業担当者が勝てる可能性の高い案件を見極め、適切な入札金額を判断するための意思決定支援システムです。

## 主な機能

### 1. 案件検索
- 全国の公共工事の入札前案件を横断検索
- 地域、規模、用途、入札方式などで絞り込み可能

### 2. 勝率予測
- 入札予定額に基づく勝率・リスクの予測
- A〜Eの5段階ランク評価
- 予測根拠とリスク要因の詳細表示

### 3. 一括予測
- 複数案件に対して同一入札額での勝率を一括計算
- 最も有望な案件を効率的に特定

### 4. 自社分析
- 過去の落札実績から強みを分析
- 地域別・用途別の実績を可視化
- 推奨戦略の提示

## セットアップ

### 必要な環境
- Python 3.8以上
- Node.js 16以上
- npm 8以上

### インストール手順

1. リポジトリをクローン
```bash
git clone https://github.com/your-repo/bid_kacho.git
cd bid_kacho
```

2. システムを起動
```bash
./run.sh
```

または個別に起動する場合：

**バックエンド:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**フロントエンド:**
```bash
cd frontend
npm install
npm start
```

## アクセス方法
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

## 使用データ
- `data/raw/mock_award_data_2000.csv`: 過去の落札実績（2000件）
- `data/raw/company_award_history.csv`: 自社の落札実績（200件）
- `data/raw/mock_tender_data_100.json`: 現在公開中の入札案件（100件）

## 技術スタック
- **バックエンド**: FastAPI, Python, Pandas, scikit-learn
- **フロントエンド**: React, Material-UI, Recharts
- **データ**: CSV, JSON形式のモックデータ

## デモ企業
- 企業名: 星田建設株式会社
- 特徴: 東京都・学校建設に強み、総合評価方式での技術点が高い