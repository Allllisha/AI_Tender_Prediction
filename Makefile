help:
	@echo "使用可能なコマンド:"
	@echo "  make build    - Dockerイメージをビルド"
	@echo "  make up       - サービスを起動"
	@echo "  make down     - サービスを停止"
	@echo "  make logs     - ログを表示"
	@echo "  make test     - テストを実行"
	@echo "  make etl      - ETL処理を手動実行"
	@echo "  make clean    - コンテナとボリュームを削除"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose exec app pytest tests/

etl:
	docker-compose exec app python app/etl/daily_batch.py --once

etl-trigger:
	curl -X POST http://localhost:8000/api/v1/etl/trigger

etl-status:
	curl http://localhost:8000/api/v1/etl/status | python -m json.tool

clean:
	docker-compose down -v
	docker system prune -f

db-shell:
	docker-compose exec postgres psql -U biduser -d bidkacho

api-docs:
	open http://localhost:8000/docs

.PHONY: help build up down logs test etl etl-trigger etl-status clean db-shell api-docs