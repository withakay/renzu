.PHONY: install test test-all lint format format-check typecheck check
.PHONY: docker-build docker-up docker-down docker-logs
.PHONY: openapi-spec clean help

# Default target
.DEFAULT_GOAL := help

# Directories
SRC_DIR := src
TEST_DIR := tests
CACHE_DIRS := .pytest_cache .ruff_cache .basedpyright .mypy_cache __pycache__

# Docker
COMPOSE_FILE := docker-compose.yml

# ------------------------------------------------------------
# Development
# ------------------------------------------------------------

install: ## Install dependencies with uv
	uv sync

test: ## Run unit tests (fast, no Docker)
	uv run pytest -m unit -v

test-all: ## Run all tests including integration (requires Docker)
	uv run pytest -v

# ------------------------------------------------------------
# Code Quality
# ------------------------------------------------------------

lint: ## Run ruff linter
	uv run ruff check $(SRC_DIR) $(TEST_DIR)

format: ## Format code with ruff
	uv run ruff format $(SRC_DIR) $(TEST_DIR)

format-check: ## Check code formatting
	uv run ruff format --check $(SRC_DIR) $(TEST_DIR)

typecheck: ## Run basedpyright type checker
	uv run basedpyright $(SRC_DIR) $(TEST_DIR)

check: lint format-check typecheck ## Run all checks (lint, format, types)

# ------------------------------------------------------------
# Docker
# ------------------------------------------------------------

docker-build: ## Build Docker images
	docker compose build

docker-up: ## Start Docker services
	docker compose up -d

docker-down: ## Stop Docker services
	docker compose down

docker-logs: ## Follow Docker logs
	docker compose logs -f

# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------

openapi-spec: ## Generate OpenAPI spec
	uv run python -m app.openapi > openapi.json

clean: ## Remove cache directories
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf $(CACHE_DIRS)

# ------------------------------------------------------------
# Help
# ------------------------------------------------------------

help: ## Show this help message
	@echo "Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Examples:"
	@echo "  make install        # Set up environment"
	@echo "  make check          # Run all quality checks"
	@echo "  make test           # Run fast unit tests"
	@echo "  make docker-up      # Start Docker stack"
