.PHONY: help install install-dev test lint format clean build docker-build docker-run docker-stop docker-clean deploy

# Directory configuration
SCRIPTS_DIR = .
BUILD_DIR = $(SCRIPTS_DIR)/build
DEPLOY_DIR = $(SCRIPTS_DIR)/deploy
CLEAN_DIR = $(SCRIPTS_DIR)/clean
REQUIREMENTS_DIR = ../requirements
CONFIG_DIR = ../config

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
	pip install -r $(REQUIREMENTS_DIR)/base.txt
	pip install -e ..

install-dev:
	pip install -r $(REQUIREMENTS_DIR)/base.txt
	pip install -r $(REQUIREMENTS_DIR)/dev.txt
	pip install -e ..

test:
	pytest ../test/ -v --cov=xtrade_ai --cov-report=html --cov-report=term-missing

lint:
	flake8 ../xtrade_ai/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 ../xtrade_ai/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	black --check --diff ../xtrade_ai/
	mypy ../xtrade_ai/ --ignore-missing-imports

format:
	black ../xtrade_ai/
	isort ../xtrade_ai/

clean:
	rm -rf ../build/
	rm -rf ../dist/
	rm -rf ../*.egg-info/
	rm -rf ../.pytest_cache/
	rm -rf ../.coverage
	rm -rf ../htmlcov/
	find .. -type d -name __pycache__ -delete
	find .. -type f -name "*.pyc" -delete

# Building
build:
	cd .. && python -m build

# Docker
docker-build:
	cd .. && docker build -t xtrade-ai -f docker/Dockerfile .

docker-run:
	cd .. && docker-compose -f docker/docker-compose.yml up -d

docker-stop:
	cd .. && docker-compose -f docker/docker-compose.yml down

docker-clean:
	cd .. && docker-compose -f docker/docker-compose.yml down -v --rmi all
	docker system prune -f

# Deployment
deploy:
	@echo "Deploying XTrade-AI Framework..."
	cd .. && docker-compose -f docker/docker-compose.yml up -d --build

# Quick start
quick-start: install-dev
	@echo "Starting XTrade-AI Framework..."
	cd .. && python -m xtrade_ai.cli --help

# Security checks
security:
	bandit -r ../xtrade_ai/
	safety check

# Documentation
docs:
	cd .. && sphinx-build -b html docs/ docs/_build/html

# Performance testing
perf-test:
	cd .. && python -m pytest test/ -m "perf" -v

# Integration testing
integration-test:
	cd .. && python -m pytest test/ -m "integration" -v

# Unit testing
unit-test:
	cd .. && python -m pytest test/ -m "unit" -v
