#!/bin/bash
# Qwen Fine-tuning Training Script
# StepUp Education Team - 2025

set -e

echo "🚀 Starting Qwen fine-tuning process..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
else
    print_warning "Virtual environment not found. Using system Python."
fi

# Set environment variables
export CUDA_VISIBLE_DEVICES=${CUDA_VISIBLE_DEVICES:-0}
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
export TOKENIZERS_PARALLELISM=false

print_status "Environment variables set:"
print_status "  CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
print_status "  PYTHONPATH: $PYTHONPATH"

# Check GPU availability
if command -v nvidia-smi &> /dev/null; then
    print_status "GPU Status:"
    nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader,nounits
else
    print_warning "nvidia-smi not found. Training will use CPU (very slow)."
fi

# Check required files
required_files=(
    "configs/training_config.yaml"
    "data/pika_data.json"
    "data/chat_template.txt"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file not found: $file"
        print_status "Creating missing files..."
        
        if [ "$file" == "data/pika_data.json" ]; then
            print_status "Creating sample training data..."
            python -c "
from src.qwen_finetune.utils.data_processor import DataProcessor
import os
os.makedirs('data', exist_ok=True)
DataProcessor.create_sample_data('data/pika_data.json', 50, 'vi')
print('✅ Sample data created')
"
        fi
    else
        print_success "Found: $file"
    fi
done

# Create output directory
mkdir -p outputs
mkdir -p models/merged

# Check disk space
available_space=$(df . | tail -1 | awk '{print $4}')
print_status "Available disk space: ${available_space}KB"

if [ "$available_space" -lt 10485760 ]; then  # 10GB in KB
    print_warning "Low disk space detected. Consider freeing up space before training."
fi

# Run training with error handling
print_status "Starting training process..."
print_status "Command: python src/qwen_finetune/training/finetune_unsloth_chatml.py"

if python src/qwen_finetune/training/finetune_unsloth_chatml.py; then
    print_success "Training completed successfully! 🎉"
    
    # Check if model was saved
    if [ -d "models/merged" ] && [ "$(ls -A models/merged)" ]; then
        print_success "Model saved to: models/merged"
        print_status "Model files:"
        ls -la models/merged/
    else
        print_warning "Model directory is empty. Check training configuration."
    fi
    
    # Show training outputs
    if [ -d "outputs" ] && [ "$(ls -A outputs)" ]; then
        print_status "Training outputs saved to: outputs/"
        ls -la outputs/
    fi
    
    print_success "Fine-tuning process completed! 🎉"
    print_status "Next steps:"
    print_status "  1. Test the model: make test"
    print_status "  2. Start serving: make serve"
    print_status "  3. Check model quality with sample queries"
    
else
    print_error "Training failed! ❌"
    print_status "Check the logs above for error details."
    print_status "Common issues:"
    print_status "  - Insufficient GPU memory (reduce batch_size in config)"
    print_status "  - CUDA out of memory (reduce max_seq_length)"
    print_status "  - Missing dependencies (run: pip install -e src/[all])"
    exit 1
fi