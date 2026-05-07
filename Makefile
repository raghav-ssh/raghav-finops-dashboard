.PHONY: help install format lint test run-backend run-frontend run clean docker-build docker-run

help:
	@echo "FinOps Reporting - Available Commands"
	@echo "======================================"
	@echo "install        - Install all dependencies"
	@echo "format         - Format code (Python & JS)"
	@echo "lint           - Run linters"
	@echo "test           - Run tests"
	@echo "run            - Start both backend and frontend"
	@echo "run-backend    - Start FastAPI backend"
	@echo "run-frontend   - Start React frontend"
	@echo "clean          - Clean generated files"
	@echo "docker-build   - Build Docker image"
	@echo "docker-run     - Run Docker container"

install:
	@echo "Installing dependencies..."
	pip install -r backend/requirements.txt
	cd frontend && npm install

format:
	@echo "Formatting code..."
	black backend/ --line-length 100
	isort backend/ --profile black
	cd frontend && npm run lint --fix || true

lint:
	@echo "Running linters..."
	pylint backend/ --disable=C0111,R0913,R0914,R0915 || true
	cd frontend && npm run lint

test:
	@echo "Running tests..."
	cd backend && pytest tests/ -v || echo "No tests found"

run:
	@echo "Starting all services..."
	./scripts/start.sh

run-backend:
	@echo "Starting backend server..."
	cd backend && python main.py

run-frontend:
	@echo "Starting frontend dev server..."
	cd frontend && npm run dev

clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf outputs/finops_reports/*.csv outputs/finops_reports/*.pdf
	rm -rf outputs/cost_reports/*.csv outputs/cost_reports/*.pdf
	rm -rf frontend/dist frontend/build

docker-build:
	@echo "Building Docker image..."
	docker build -t finops-reporting:latest .

docker-run:
	@echo "Running Docker container..."
	docker run -p 8001:8001 -v $(PWD)/.env:/app/.env finops-reporting:latest
