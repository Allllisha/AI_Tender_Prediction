#!/bin/bash
# Seed data script for Docker PostgreSQL
# DockerコンテナからPostgreSQLに接続してseedデータを投入

echo "🚀 Dockerコンテナ内でseedデータ投入開始"

# Pythonスクリプトをコンテナ内にコピーして実行
docker cp /Users/anemoto/bid_kacho/backend/seed_data.py bid-backend:/tmp/seed_data.py
docker cp /Users/anemoto/bid_kacho/data bid-backend:/tmp/

# コンテナ内でスクリプトを実行
docker exec bid-backend sh -c "cd /tmp && DATABASE_URL=postgresql://bid_user:bid_password_2024@postgres:5432/bid_kacho_db python seed_data.py"

echo "✅ Dockerコンテナ内でのseedデータ投入完了"