# マルチステージビルド
# ステージ1: ビルド
FROM node:18-alpine AS builder

WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm ci

# アプリケーションコードをコピー
COPY . .

# 本番用ビルド
RUN npm run build

# ステージ2: 本番環境
FROM node:18-alpine

WORKDIR /app

# serve パッケージをインストール（静的ファイルサーバー）
RUN npm install -g serve

# ビルド済みファイルをコピー
COPY --from=builder /app/build ./build

# ポート3000を公開
EXPOSE 3000

# 静的ファイルをserveで配信
CMD ["serve", "-s", "build", "-l", "3000"]