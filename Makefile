# Makefile for Forró Media Crawler
init:
	mkdir -p ./data/navidrome ./data/media ./data
	
PYTHONPATH := /app

# Default target: run everything
up:
	docker-compose up --build
	

# Run just the API (control panel)
api:
	docker-compose up --build api

# Run the crawler once manually
crawl:
	docker-compose run --rm -e PYTHONPATH=$(PYTHONPATH) crawler python apps/crawler/crawler.py

# Build/rebuild all images
build:
	docker-compose build

rebuild:
	docker-compose build && docker-compose up

# Stop all services
down:
	docker-compose down

# Show API logs
logs:
	docker-compose logs -f api

# Show crawler logs
logs-crawler:
	docker-compose logs -f crawler

# Restart the API container
restart-api:
	docker-compose restart api

# Reset crawl state (optional future endpoint)
reset:
	curl -X POST http://localhost:8000/reset