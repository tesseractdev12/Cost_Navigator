infrastructure-build:
	docker-compose build

infrastructure-up:
	docker-compose up --build

env:
	cp .env.example .env

seed:
	docker-compose exec app bash scripts/seed.sh 

chmod:
	chmod +x scripts/run.sh scripts/seed.sh

infrastructure-down:
	docker-compose down -v