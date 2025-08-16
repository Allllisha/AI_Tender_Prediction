# マルチステージビルド
# ステージ1: ビルド
FROM node:18-alpine AS builder

WORKDIR /app

# package.jsonをコピー
COPY package.json ./

# 依存関係をインストール
RUN npm install

# アプリケーションコードをコピー
COPY . .

# ビルド時の環境変数を設定（Vite用）
# デフォルトはAzure用のURL
ARG VITE_API_URL=https://app-bid-kacho-backend.azurewebsites.net
ENV VITE_API_URL=$VITE_API_URL

# 本番用ビルド
RUN npm run build

# ステージ2: 本番環境
FROM node:18-alpine

WORKDIR /app

# serve パッケージをインストール（静的ファイルサーバー）
RUN npm install -g serve

# ビルド済みファイルをコピー（Viteはbuildディレクトリに出力）
COPY --from=builder /app/build ./build

# ポート3000を公開
EXPOSE 3000

# 静的ファイルをserveで配信
CMD ["serve", "-s", "build", "-l", "3000"]