# Application configuration
APP_NAME = status-service
PORT ?= 8000
DATA_DIR ?= $(PWD)/data

# Docker configuration
DOCKER_IMAGE = $(APP_NAME)
DOCKER_TEST_IMAGE = $(APP_NAME)-tests

# Declare phony targets (targets that don't represent files)
.PHONY: test build run stop clean help

# Show help by default
.DEFAULT_GOAL := help

# Build the application Docker image
build: ## Build the production Docker image
	@echo "Building production Docker image..."
	docker build -t $(DOCKER_IMAGE) .

# Build the test Docker image
build-test: ## Build the test Docker image
	@echo "Building test Docker image..."
	docker build -f Dockerfile.test -t $(DOCKER_TEST_IMAGE) .

# Run tests in Docker
test: build-test ## Run tests in Docker
	@echo "Running tests..."
	docker run --rm $(DOCKER_TEST_IMAGE)

# Run the application in Docker
run: build ## Run the application container (use PORT=xxxx to override default port)
	@echo "Starting application on port $(PORT)..."
	@mkdir -p $(DATA_DIR)
	docker run --rm -d \
		-p $(PORT):8000 \
		-v $(DATA_DIR):/app/data \
		--name $(APP_NAME) \
		$(DOCKER_IMAGE)
	@echo "Application started! Access it at http://localhost:$(PORT)"

# Stop the running container
stop: ## Stop the running application container
	@echo "Stopping application..."
	docker stop -t 0 $(APP_NAME) || true
	docker rm -f $(APP_NAME) || true

# Clean up Docker resources
clean: stop ## Clean up all Docker resources
	@echo "Cleaning up Docker resources..."
	docker rmi $(DOCKER_IMAGE) $(DOCKER_TEST_IMAGE) || true
	@echo "Cleanup complete!"

# Help target
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk '/^[a-zA-Z_-]+:.*?## .*$$/ {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)