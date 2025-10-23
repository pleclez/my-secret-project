.PHONY: help install test run docker-build docker-up clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make run          - Run development server"
	@echo "  make init-db      - Initialize database schema"
	@echo "  make seed-db      - Seed database with sample data"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make clean        - Clean cache and temporary files"

install:
	pip install -r requirements.txt

test:
	pytest tests/

test-cov:
	pytest --cov=src --cov-report=html tests/

run:
	python app.py

init-db:
	python scripts/init_db.py

seed-db:
	python scripts/seed_data.py

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

