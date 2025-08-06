#!/bin/bash
# Environment Setup Script with Python Version Detection
# StepUp Education Team - 2025

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

print_status "🔧 Setting up Qwen fine-tuning environment..."

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_status "🐍 Detected Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies based on Python version
if python -c "import sys; exit(0 if sys.version_info < (3, 13) else 1)" 2>/dev/null; then
    print_success "✅ Python <3.13 detected - Installing with Unsloth support"
    print_status "📦 Installing core dependencies..."
    pip install -e "src/"
    
    print_status "📦 Installing Unsloth (this may take a while)..."
    pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
    
    print_success "✅ Unsloth training environment ready!"
    echo "    Training method: Unsloth + LoRA"
    echo "    Script: finetune_unsloth_chatml.py"
    
else
    print_warning "⚠️  Python 3.13+ detected - Unsloth not compatible"
    print_status "📦 Installing standard LoRA dependencies..."
    pip install -e "src/[core]"
    
    print_success "✅ Standard LoRA training environment ready!"
    echo "    Training method: Standard PyTorch + LoRA"
    echo "    Script: finetune_standard_lora.py"
fi

# Install optional dependencies
print_status "📦 Installing optional dependencies..."
pip install bitsandbytes || print_warning "bitsandbytes installation failed (optional for quantization)"

# Create sample data
print_status "📊 Creating sample training data..."
python -c "
import json
import os
os.makedirs('data', exist_ok=True)
sample_data = []
for i in range(20):
    conversations = [
        {'role': 'user', 'content': f'Xin chào! Đây là câu hỏi số {i+1}. Bạn có thể giúp tôi không?'},
        {'role': 'assistant', 'content': f'Chào bạn! Tôi rất sẵn lòng giúp bạn với câu hỏi số {i+1}. Đây là câu trả lời mẫu.'}
    ]
    sample_data.append({'conversations': conversations})

with open('data/pika_data.json', 'w', encoding='utf-8') as f:
    json.dump(sample_data, f, ensure_ascii=False, indent=2)

print('✅ Created sample data: data/pika_data.json')
"

# Environment summary
print_success "🎉 Environment setup completed!"
echo ""
print_status "📋 Setup Summary:"
print_status "  Python version: $PYTHON_VERSION"
print_status "  Virtual environment: venv/"
print_status "  Training data: data/pika_data.json"
print_status "  Configuration: configs/"
echo ""
print_status "🚀 Next steps:"
print_status "  1. Activate environment: source venv/bin/activate"
print_status "  2. Configure training: edit configs/training_config.yaml"
print_status "  3. Start training: make train"
print_status "  4. Start serving: make serve"
echo ""

# Check GPU
if command -v nvidia-smi &> /dev/null; then
    print_status "🖥️  GPU Status:"
    nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader,nounits
else
    print_warning "⚠️  No NVIDIA GPU detected. Training will be slow on CPU."
fi