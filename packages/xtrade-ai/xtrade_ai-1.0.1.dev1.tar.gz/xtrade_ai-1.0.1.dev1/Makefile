.PHONY: help install install-dev test lint format clean build docker-build docker-run docker-stop docker-clean deploy

# Default target
help:
	@echo "XTrade-AI Framework - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests with coverage"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean build artifacts"
	@echo ""
	@echo "Building:"
	@echo "  build        - Build Python package"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run Docker containers"
	@echo "  docker-stop  - Stop Docker containers"
	@echo "  docker-clean - Clean Docker containers and images"
	@echo ""
	@echo "Deployment:"
	@echo "  deploy       - Deploy to production"

# Development
install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest test/ -v --cov=xtrade_ai --cov-report=html --cov-report=term-missing

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	black --check --diff .
	mypy . --ignore-missing-imports

format:
	black .
	isort .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Building
build:
	python -m build

# Docker
docker-build:
	docker build -t xtrade-ai .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-clean:
	docker-compose down -v --rmi all
	docker system prune -f

# Deployment
deploy:
	@echo "Deploying XTrade-AI Framework..."
	docker-compose -f docker-compose.yml up -d --build

# Quick start
quick-start: install-dev
	@echo "Starting XTrade-AI Framework..."
	python -m xtrade_ai.cli --help

# Security checks
security:
	bandit -r xtrade_ai/
	safety check

# Documentation
docs:
	sphinx-build -b html docs/ docs/_build/html

# Performance testing
perf-test:
	python -m pytest test/ -m "perf" -v

# Integration testing
integration-test:
	python -m pytest test/ -m "integration" -v

# Unit testing
unit-test:
	python -m pytest test/ -m "unit" -v
