.PHONY: help clean build check test deploy install-dev install-test install-docs

help: ## Show this help message
	@echo "XTrade-AI Framework Build and Deploy Commands"
	@echo "============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean ## Build the package
	@echo "🔨 Building package..."
	python -m build

check: build ## Check the built package
	@echo "✅ Checking package..."
	twine check dist/*

test: check ## Upload to TestPyPI
	@echo "🚀 Uploading to TestPyPI..."
	twine upload --repository testpypi dist/*

deploy: check ## Upload to PyPI
	@echo "🚀 Uploading to PyPI..."
	twine upload dist/*

install-dev: ## Install development dependencies
	@echo "📦 Installing development dependencies..."
	pip install -r requirements/dev.txt
	pip install -e .

install-test: ## Install test dependencies
	@echo "📦 Installing test dependencies..."
	pip install -r requirements/dev.txt

install-docs: ## Install documentation dependencies
	@echo "📦 Installing documentation dependencies..."
	pip install sphinx sphinx-rtd-theme myst-parser

test-unit: ## Run unit tests
	@echo "🧪 Running unit tests..."
	pytest test/ -v -m "not integration and not slow"

test-integration: ## Run integration tests
	@echo "🧪 Running integration tests..."
	pytest test/ -v -m "integration"

test-all: ## Run all tests
	@echo "🧪 Running all tests..."
	pytest test/ -v

lint: ## Run linting
	@echo "🔍 Running linting..."
	black xtrade_ai/ test/ --check
	isort xtrade_ai/ test/ --check-only
	flake8 xtrade_ai/ test/
	mypy xtrade_ai/

format: ## Format code
	@echo "🎨 Formatting code..."
	black xtrade_ai/ test/
	isort xtrade_ai/ test/

docs: ## Build documentation
	@echo "📚 Building documentation..."
	cd docs && make html

docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	cd docs/_build/html && python -m http.server 8000

docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t xtrade-ai:latest -f docker/Dockerfile .

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker run -p 8000:8000 xtrade-ai:latest

docker-compose-up: ## Start with docker-compose
	@echo "🐳 Starting with docker-compose..."
	docker-compose up -d

docker-compose-down: ## Stop docker-compose
	@echo "🐳 Stopping docker-compose..."
	docker-compose down

security-check: ## Run security checks
	@echo "🔒 Running security checks..."
	bandit -r xtrade_ai/
	safety check

pre-commit: ## Run pre-commit hooks
	@echo "🔧 Running pre-commit hooks..."
	pre-commit run --all-files

setup-pre-commit: ## Setup pre-commit hooks
	@echo "🔧 Setting up pre-commit hooks..."
	pre-commit install

version: ## Show current version
	@python -c "import xtrade_ai; print(xtrade_ai.__version__)"

requirements: ## Generate requirements files
	@echo "📋 Generating requirements files..."
	pip-compile requirements/base.in -o requirements/base.txt
	pip-compile requirements/dev.in -o requirements/dev.txt
	pip-compile requirements/ta.in -o requirements/ta.txt
	pip-compile requirements/viz.in -o requirements/viz.txt
	pip-compile requirements/monitor.in -o requirements/monitor.txt
	pip-compile requirements/performance.in -o requirements/performance.txt
	pip-compile requirements/database.in -o requirements/database.txt
	pip-compile requirements/api.in -o requirements/api.txt
