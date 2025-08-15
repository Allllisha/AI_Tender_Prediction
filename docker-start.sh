#!/bin/bash

echo "======================================"
echo "建築入札インテリジェンス・システム"
echo "Docker版 起動"
echo "======================================"

# 既存のコンテナを停止・削除
echo "既存のコンテナをクリーンアップ中..."
docker-compose down

# イメージをビルド
echo "Dockerイメージをビルド中..."
docker-compose build

# コンテナを起動
echo "コンテナを起動中..."
docker-compose up -d

# ヘルスチェック
echo ""
echo "システムの起動を待っています..."
sleep 10

# APIの状態を確認
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ バックエンドAPI: 正常起動"
else
    echo "❌ バックエンドAPI: 起動失敗"
fi

echo ""
echo "======================================"
echo "起動完了！"
echo ""
echo "🌐 フロントエンド: http://localhost:3000"
echo "🔧 バックエンドAPI: http://localhost:8000"
echo "📚 APIドキュメント: http://localhost:8000/docs"
echo ""
echo "ログ確認: docker-compose logs -f"
echo "停止: docker-compose down"
echo "======================================"