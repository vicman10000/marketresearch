.PHONY: help build run test full clean logs shell validate

# Default target
help:
	@echo "Market Research Visualization - Docker Commands"
	@echo "================================================"
	@echo ""
	@echo "Quick Start:"
	@echo "  make build          Build the Docker image"
	@echo "  make run            Run with 30 stocks (default)"
	@echo "  make test           Run with sample data (fast)"
	@echo "  make full           Run full S&P 500 analysis"
	@echo ""
	@echo "Development:"
	@echo "  make shell          Open interactive shell in container"
	@echo "  make logs           Show container logs"
	@echo "  make validate       Validate Docker configuration"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          Remove containers and images"
	@echo "  make clean-all      Remove everything including volumes"
	@echo ""
	@echo "Custom:"
	@echo "  make run ARGS='--max-stocks 50 --animation-period W'"
	@echo ""

# Build the Docker image
build:
	@echo "Building Docker image..."
	docker-compose build

# Run with default settings (30 stocks)
run:
	@echo "Running market visualization (30 stocks)..."
	docker-compose up market-viz

# Run with sample data (fast test)
test:
	@echo "Running test with sample data..."
	docker-compose --profile test up market-viz-test

# Run full S&P 500 analysis
full:
	@echo "Running full S&P 500 analysis..."
	docker-compose --profile full up market-viz-full

# Run with custom arguments
custom:
	@echo "Running with custom arguments: $(ARGS)"
	docker-compose run market-viz $(ARGS)

# Open interactive shell
shell:
	@echo "Opening interactive shell..."
	docker-compose run --entrypoint /bin/bash market-viz

# Show logs
logs:
	docker-compose logs -f market-viz

# Validate configuration
validate:
	@echo "Validating Docker configuration..."
	@./test_docker_config.sh

# Clean up containers
clean:
	@echo "Removing containers and images..."
	docker-compose down
	docker rmi market-research-visualization:latest || true

# Clean everything including volumes
clean-all:
	@echo "Removing everything..."
	docker-compose down -v
	docker rmi market-research-visualization:latest || true
	@echo "Cleaning output directories..."
	rm -rf outputs/static/*.html
	rm -rf outputs/animated/*.html
	rm -rf data/cache/*.csv

# View results
view-static:
	@echo "Opening static dashboard..."
	@if [ -f outputs/static/dashboard.html ]; then \
		xdg-open outputs/static/dashboard.html 2>/dev/null || \
		open outputs/static/dashboard.html 2>/dev/null || \
		echo "Please open outputs/static/dashboard.html in your browser"; \
	else \
		echo "No dashboard found. Run 'make run' first."; \
	fi

view-animated:
	@echo "Opening animated bubble chart..."
	@if [ -f outputs/animated/animated_bubble_chart.html ]; then \
		xdg-open outputs/animated/animated_bubble_chart.html 2>/dev/null || \
		open outputs/animated/animated_bubble_chart.html 2>/dev/null || \
		echo "Please open outputs/animated/animated_bubble_chart.html in your browser"; \
	else \
		echo "No animation found. Run 'make run' first."; \
	fi

# Quick demo workflow
demo:
	@echo "Running complete demo..."
	@echo "1. Building image..."
	@make build
	@echo ""
	@echo "2. Running test with sample data..."
	@make test
	@echo ""
	@echo "3. Opening visualizations..."
	@make view-static
	@make view-animated

# Check Docker installation
check-docker:
	@command -v docker >/dev/null 2>&1 || { echo "Docker is not installed. Please install Docker first."; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose is not installed. Please install Docker Compose first."; exit 1; }
	@echo "✓ Docker and Docker Compose are installed"
	@docker --version
	@docker-compose --version
