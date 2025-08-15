# 建築入札インテリジェンス・システム - Docker版

## Docker環境での起動方法

### 前提条件
- Docker Desktop がインストールされていること
- Docker Compose がインストールされていること

### 起動手順

#### 1. 簡単起動（推奨）
```bash
# Dockerコンテナをビルド・起動
./docker-start.sh
```

#### 2. 手動起動
```bash
# イメージをビルド
docker-compose build

# コンテナを起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

### アクセス方法
- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs

### 停止方法
```bash
# 簡単停止
./docker-stop.sh

# または手動停止
docker-compose down
```

### トラブルシューティング

#### ポートが使用中の場合
```bash
# 既存のプロセスを確認
lsof -i :3000
lsof -i :8000

# 必要に応じて既存プロセスを停止
kill -9 [PID]
```

#### コンテナの状態確認
```bash
# コンテナの状態を確認
docker-compose ps

# ログを確認
docker-compose logs backend
docker-compose logs frontend
```

#### 完全リセット
```bash
# コンテナ、イメージ、ボリュームを削除
docker-compose down -v --rmi all

# 再ビルド
docker-compose build --no-cache
docker-compose up -d
```

### 開発モード
```bash
# ライブリロード有効で起動
docker-compose up
```

### システム構成
- **backend**: FastAPI (Python 3.11)
  - ポート: 8000
  - 入札データ処理、予測アルゴリズム
  
- **frontend**: React (Node.js 18)
  - ポート: 3000
  - Material-UI使用のWebインターフェース

### データ
- `/data/raw/`: モックデータ格納
  - `mock_award_data_2000.csv`: 過去の落札実績
  - `company_award_history.csv`: 星田建設の実績
  - `mock_tender_data_100.json`: 入札前案件

### 環境変数
- `REACT_APP_API_URL`: バックエンドAPIのURL（デフォルト: http://localhost:8000）