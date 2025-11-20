# Makefile for Logistics KPI Prediction System (Windows)

.PHONY: help install test run-api run-dashboard run-all stop clean docker-build docker-up docker-down format lint

help:
	@echo "Logistics KPI Prediction System - Commands"
	@echo "==========================================="
	@echo "install       - Install dependencies"
	@echo "test          - Run tests"
	@echo "run-api       - Start API server"
	@echo "run-dashboard - Start dashboard"
	@echo "run-all       - Start all services"
	@echo "stop          - Stop all services"
	@echo "clean         - Clean cache files"
	@echo "docker-build  - Build Docker images"
	@echo "docker-up     - Start Docker containers"
	@echo "docker-down   - Stop Docker containers"
	@echo "format        - Format code with black"
	@echo "lint          - Lint code with flake8"

install:
	python -m venv .venv
	.\.venv\Scripts\activate && pip install -r deployment\requirements.txt

test:
	.\.venv\Scripts\activate && python -m pytest tests/ -v

run-api:
	.\.venv\Scripts\activate && python src\api\app.py

run-dashboard:
	.\.venv\Scripts\activate && streamlit run src\dashboard\dashboard.py

run-all:
	scripts\startup.bat

stop:
	scripts\shutdown.bat

clean:
	powershell -Command "Remove-Item -Recurse -Force __pycache__, .pytest_cache, .coverage, htmlcov, *.egg-info, build, dist -ErrorAction SilentlyContinue"
	powershell -Command "Get-ChildItem -Recurse -Include __pycache__ | Remove-Item -Recurse -Force"

docker-build:
	docker-compose -f deployment\docker-compose.yml build

docker-up:
	docker-compose -f deployment\docker-compose.yml up -d

docker-down:
	docker-compose -f deployment\docker-compose.yml down

format:
	.\.venv\Scripts\activate && black src tests

lint:
	.\.venv\Scripts\activate && flake8 src tests
