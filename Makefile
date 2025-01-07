# Application configuration
APP_NAME = status-service
DATA_DIR ?= $(PWD)/data

# Docker configuration
DOCKER_TEST_IMAGE = $(APP_NAME)-tests

# Declare phony targets (targets that don't represent files)
.PHONY: test build run stop clean help dev logs

# Show help by default
.DEFAULT_GOAL := help

# Build all Docker images
build: ## Build all Docker images
	@echo "Building Docker images..."
	docker-compose build

# Build the test Docker image
build-test: ## Build the test Docker image
	@echo "Building test Docker image..."
	docker build -f Dockerfile.test -t $(DOCKER_TEST_IMAGE) .

# Run tests in Docker
test: build-test ## Run tests in Docker
	@echo "Running tests..."
	docker run --rm $(DOCKER_TEST_IMAGE)

# Run the application in Docker
run: ## Run the application (frontend and backend)
	@echo "Starting application..."
	@mkdir -p $(DATA_DIR)
	docker-compose up -d
	@echo "Application started!"
	@echo "Frontend: http://localhost"
	@echo "Backend API: http://localhost:8000"

# View application logs
logs: ## View application logs
	docker-compose logs -f

# Stop the application
stop: ## Stop the application
	@echo "Stopping application..."
	docker-compose down -v

# Clean up Docker resources
clean: stop ## Clean up all Docker resources
	@echo "Cleaning up Docker resources..."
	docker-compose down -v --rmi all
	docker rmi $(DOCKER_TEST_IMAGE) || true
	@echo "Cleanup complete!"

# Development mode with live reload
dev: ## Run application in development mode
	@echo "Starting application in development mode..."
	@mkdir -p $(DATA_DIR)
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Help target
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk '/^[a-zA-Z_-]+:.*?## .*$$/ {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)