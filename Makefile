# Qwen Fine-tuning Toolkit Makefile
# StepUp Education Team - 2025

.PHONY: help install setup data train serve test clean lint format docker-build docker-run

# Default target
help:
	@echo "🔧 Qwen Fine-tuning Toolkit - Available Commands:"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make setup          - Complete project setup (venv + install + data)"
	@echo "  make install        - Install Python dependencies"
	@echo "  make install-dev    - Install with development dependencies"
	@echo ""
	@echo "📊 Data Management:"
	@echo "  make data           - Create sample training data"
	@echo "  make validate-data  - Validate training data format"
	@echo "  make analyze-data   - Analyze data statistics"
	@echo ""
	@echo "🚀 Training & Serving:"
	@echo "  make train          - Run fine-tuning training"
	@echo "  make serve          - Start vLLM serving server"
	@echo "  make test-api       - Test the serving API"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean          - Clean up generated files"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code with black"
	@echo "  make test           - Run unit tests"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run with Docker"
	@echo ""

# Setup complete development environment
setup:
	@echo "🔧 Setting up Qwen fine-tuning environment..."
	@echo "🐍 Checking Python version..."
	@python3 -c "import sys; print(f'Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
	python3 -m venv venv
	@echo "📦 Installing dependencies..."
	./venv/bin/pip install --upgrade pip setuptools wheel
	@echo "🔍 Detecting Python version for dependency installation..."
	@if ./venv/bin/python -c "import sys; exit(0 if sys.version_info < (3, 13) else 1)" 2>/dev/null; then \
		echo "📦 Installing with Unsloth support (Python <3.13)..."; \
		./venv/bin/pip install -e "src/[all]"; \
	else \
		echo "📦 Installing core dependencies (Python 3.13+, Unsloth not compatible)..."; \
		./venv/bin/pip install -e "src/[core]"; \
	fi
	@echo "📊 Creating sample data..."
	$(MAKE) data
	@echo "✅ Setup completed!"
	@echo ""
	@echo "🎉 Next steps:"
	@echo "  1. Activate environment: source venv/bin/activate"
	@echo "  2. Start training: make train"
	@echo "  3. Start serving: make serve"

# Install Python dependencies
install:
	pip install --upgrade pip setuptools wheel
	pip install -e src/

# Install with development dependencies
install-dev:
	pip install --upgrade pip setuptools wheel
	pip install -e "src/[all]"

# Create sample training data
data:
	@echo "📊 Creating sample training data..."
	mkdir -p data
	python -c "\
from src.qwen_finetune.utils.data_processor import DataProcessor; \
DataProcessor.create_sample_data('data/pika_data.json', 50, 'vi'); \
print('✅ Sample data created: data/pika_data.json')"

# Validate training data
validate-data:
	@echo "🔍 Validating training data..."
	python -c "\
from src.qwen_finetune.utils.data_processor import DataProcessor; \
result = DataProcessor.validate_data('data/pika_data.json'); \
print('✅ Validation PASSED' if result else '❌ Validation FAILED')"

# Analyze training data
analyze-data:
	@echo "📈 Analyzing training data..."
	python -c "\
from src.qwen_finetune.utils.data_processor import DataProcessor; \
DataProcessor.analyze_data('data/pika_data.json')"

# Run training
train:
	@echo "🚀 Starting fine-tuning training..."
	@echo "🔍 Detecting Python version for training method..."
	@if python -c "import sys; exit(0 if sys.version_info < (3, 13) else 1)" 2>/dev/null; then \
		echo "📦 Using Unsloth training (Python <3.13)..."; \
		chmod +x scripts/train.sh; \
		./scripts/train.sh; \
	else \
		echo "📦 Using standard LoRA training (Python 3.13+)..."; \
		python src/qwen_finetune/training/finetune_standard_lora.py; \
	fi

# Start serving
serve:
	@echo "🌐 Starting vLLM serving server..."
	chmod +x scripts/serve.sh
	./scripts/serve.sh

# Test the API
test-api:
	@echo "🔍 Testing serving API..."
	@echo "Testing health endpoint..."
	curl -s http://localhost:8000/health | python -m json.tool || echo "❌ Health check failed"
	@echo ""
	@echo "Testing chat completion..."
	curl -s -X POST http://localhost:8000/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d '{"messages": [{"role": "user", "content": "Xin chào! Bạn có khỏe không?"}], "max_tokens": 100}' \
		| python -m json.tool || echo "❌ Chat completion failed"

# Run unit tests
test:
	@echo "🧪 Running tests..."
	python -c "\
from src.qwen_finetune.utils.data_processor import DataProcessor; \
print('Testing data processor...'); \
DataProcessor.create_sample_data('test_data.json', 5); \
result = DataProcessor.validate_data('test_data.json'); \
print('✅ Data processor test PASSED' if result else '❌ Data processor test FAILED'); \
import os; os.remove('test_data.json')"

# Clean up generated files
clean:
	@echo "🧹 Cleaning up..."
	rm -rf outputs/
	rm -rf models/merged/
	rm -rf __pycache__/
	rm -rf src/**/__pycache__/
	rm -rf .pytest_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*~" -delete
	@echo "✅ Cleanup completed!"

# Lint code
lint:
	@echo "🔍 Running code linting..."
	python -m flake8 src/ --max-line-length=100 --ignore=E203,W503 || echo "⚠️ Linting issues found"
	python -m mypy src/ --ignore-missing-imports || echo "⚠️ Type checking issues found"

# Format code
format:
	@echo "✨ Formatting code..."
	python -m black src/ --line-length=100
	python -m isort src/ --profile black

# Build Docker image
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -f deployment/Dockerfile -t qwen-finetune:latest .

# Run with Docker
docker-run:
	@echo "🐳 Running with Docker..."
	docker-compose -f deployment/docker-compose.yml up

# Quick development cycle
dev: clean data train

# Production deployment preparation
prod-prep: clean install data validate-data lint

# Show project status
status:
	@echo "📊 Project Status:"
	@echo ""
	@echo "📂 Directory structure:"
	@find . -type f -name "*.py" | head -10
	@echo ""
	@echo "📊 Data files:"
	@ls -la data/ 2>/dev/null || echo "No data directory"
	@echo ""
	@echo "🤖 Model files:"
	@ls -la models/ 2>/dev/null || echo "No models directory"
	@echo ""
	@echo "🔧 Configuration:"
	@ls -la configs/ 2>/dev/null || echo "No configs directory"

# Show GPU status
gpu:
	@echo "🖥️ GPU Status:"
	@nvidia-smi 2>/dev/null || echo "No NVIDIA GPU detected"

# Environment info
env:
	@echo "🌍 Environment Information:"
	@echo "Python version: $(shell python --version)"
	@echo "Pip version: $(shell pip --version)"
	@echo "Current directory: $(shell pwd)"
	@echo "CUDA_VISIBLE_DEVICES: $(CUDA_VISIBLE_DEVICES)"