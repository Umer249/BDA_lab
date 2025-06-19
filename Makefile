# AutoML Web Application Makefile

.PHONY: help install run test docker-build docker-run docker-compose-up docker-compose-down clean deploy-azure lint format

# Default target
help:
	@echo "Available targets:"
	@echo "  install          Install Python dependencies"
	@echo "  run             Run the Streamlit application locally"
	@echo "  test            Run tests (when implemented)"
	@echo "  docker-build    Build Docker image"
	@echo "  docker-run      Run Docker container"
	@echo "  docker-compose-up   Start with Docker Compose"
	@echo "  docker-compose-down Stop Docker Compose"
	@echo "  deploy-azure    Deploy to Azure (requires Azure CLI)"
	@echo "  clean           Clean up generated files"
	@echo "  lint            Run code linting"
	@echo "  format          Format code with black"
	@echo "  setup           Initial project setup"

# Python environment setup
install:
	pip install -r requirements.txt

# Development
run:
	streamlit run app.py --server.port 8501

test:
	@echo "Tests not implemented yet"
	# python -m pytest tests/

lint:
	flake8 src/ app.py
	pylint src/ app.py

format:
	black src/ app.py
	isort src/ app.py

# Docker commands
docker-build:
	docker build -t automl-app .

docker-run:
	docker run -p 8501:8501 \
	  -v $(PWD)/models:/app/models \
	  -v $(PWD)/reports:/app/reports \
	  -v $(PWD)/data:/app/data \
	  automl-app

docker-compose-up:
	docker-compose up --build -d

docker-compose-down:
	docker-compose down

# Azure deployment
deploy-azure:
	chmod +x deployment/azure/deploy.sh
	./deployment/azure/deploy.sh

# Utility commands
setup:
	mkdir -p models reports data logs
	cp .env.example .env
	@echo "Project setup complete!"
	@echo "1. Edit .env file with your configuration"
	@echo "2. Run 'make install' to install dependencies"
	@echo "3. Run 'make run' to start the application"

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	@echo "Cleaned up generated files"

# Development environment
dev-setup:
	python -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "source venv/bin/activate  # On Unix/macOS"
	@echo "venv\\Scripts\\activate    # On Windows"

# Production commands
prod-run:
	streamlit run app.py \
	  --server.port 8501 \
	  --server.address 0.0.0.0 \
	  --server.headless true \
	  --browser.gatherUsageStats false

# Backup and restore
backup-models:
	tar -czf models-backup-$(shell date +%Y%m%d_%H%M%S).tar.gz models/
	@echo "Models backed up"

restore-models:
	@echo "Usage: make restore-models BACKUP=models-backup-YYYYMMDD_HHMMSS.tar.gz"
	tar -xzf $(BACKUP) -C .

# Health check
health-check:
	curl -f http://localhost:8501/_stcore/health || echo "Application not running"

# Documentation
docs:
	@echo "Documentation is in README.md"
	@echo "API documentation can be generated with sphinx (not implemented)"

# Version management
version:
	@echo "AutoML Web Application v1.0.0"

# Quick start
quickstart: setup install run 