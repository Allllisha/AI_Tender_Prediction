#!/bin/bash

echo "=========================================="
echo "建築入札インテリジェンス・システム デモ起動"
echo "=========================================="

# Kill any existing processes on ports
echo "既存のプロセスをクリーンアップ中..."
pkill -f "python main.py" 2>/dev/null
pkill -f "npm start" 2>/dev/null
sleep 2

# Start backend
echo "バックエンドを起動中..."
cd backend
python main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "バックエンド PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend
echo "フロントエンドを起動中..."
cd ../frontend
npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "フロントエンド PID: $FRONTEND_PID"

echo ""
echo "=========================================="
echo "システム起動完了！"
echo ""
echo "フロントエンド: http://localhost:3000"
echo "バックエンドAPI: http://localhost:8000"
echo "APIドキュメント: http://localhost:8000/docs"
echo ""
echo "デモ企業: 星田建設株式会社"
echo "=========================================="
echo ""
echo "終了: Ctrl+C または ./stop_demo.sh"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'システムを停止しました'; exit" INT
wait