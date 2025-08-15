-- ユーザー作成（PostgreSQL初期化時）
-- このファイルは01_init.sqlより先に実行されます

-- データベースのユーザーとロールを作成
-- （docker-compose.ymlで指定したユーザーと同じものを使用）
-- ユーザーは環境変数で既に作成されているはずですが、念のため権限を付与

-- bid_userにすべての権限を付与
GRANT ALL PRIVILEGES ON DATABASE bid_kacho_db TO bid_user;