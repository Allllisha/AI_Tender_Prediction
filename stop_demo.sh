#!/bin/bash

echo "システムを停止中..."
pkill -f "python main.py"
pkill -f "npm start"
echo "停止完了"