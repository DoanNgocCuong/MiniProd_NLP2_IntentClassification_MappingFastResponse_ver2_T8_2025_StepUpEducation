#!/bin/bash
# Qwen vLLM Serving Script
# StepUp Education Team - 2025

set -e

echo "🌐 Starting Qwen vLLM serving server..."

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

print_status "Environment variables set:"
print_status "  CUDA_VISIBLE_DEVICES: $CUDA_VISIBLE_DEVICES"
print_status "  PYTHONPATH: $PYTHONPATH"

# Check GPU availability
if command -v nvidia-smi &> /dev/null; then
    print_status "GPU Status:"
    nvidia-smi --query-gpu=index,name,memory.used,memory.total --format=csv,noheader,nounits
else
    print_warning "nvidia-smi not found. Server will use CPU (very slow)."
fi

# Check required files
required_files=(
    "configs/serving_config.yaml"
)

# Check if model exists
MODEL_PATH="models/merged"
if [ ! -d "$MODEL_PATH" ] || [ ! "$(ls -A $MODEL_PATH)" ]; then
    print_error "Model not found at: $MODEL_PATH"
    print_status "Please ensure you have:"
    print_status "  1. Completed training: make train"
    print_status "  2. Or downloaded a pre-trained model to $MODEL_PATH"
    print_status "  3. Model directory should contain config.json and pytorch_model.bin"
    exit 1
else
    print_success "Found model at: $MODEL_PATH"
    print_status "Model files:"
    ls -la "$MODEL_PATH" | head -10
fi

# Check config file
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file not found: $file"
        exit 1
    else
        print_success "Found: $file"
    fi
done

# Parse config for server details
HOST=$(python -c "
import yaml
with open('configs/serving_config.yaml', 'r') as f:
    config = yaml.safe_load(f) or {}
print(config.get('host', '0.0.0.0'))
" 2>/dev/null || echo "0.0.0.0")

PORT=$(python -c "
import yaml
with open('configs/serving_config.yaml', 'r') as f:
    config = yaml.safe_load(f) or {}
print(config.get('port', 8000))
" 2>/dev/null || echo "8000")

print_status "Server configuration:"
print_status "  Host: $HOST"
print_status "  Port: $PORT"
print_status "  Model: $MODEL_PATH"

# Check if port is available
if command -v lsof &> /dev/null; then
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null; then
        print_warning "Port $PORT is already in use. Please stop the existing service or change the port."
        print_status "To kill existing service: lsof -ti:$PORT | xargs kill"
    fi
fi

# Function to handle cleanup
cleanup() {
    print_status "Shutting down server..."
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start the server
print_status "Starting vLLM server..."
print_status "Command: python src/qwen_finetune/serving/vllm_server.py"
print_status ""
print_success "🚀 Server will start at: http://$HOST:$PORT"
print_success "📚 API docs will be at: http://$HOST:$PORT/docs"
print_success "🔍 Health check: http://$HOST:$PORT/health"
print_status ""
print_status "To test the API, run in another terminal:"
print_status "  curl -X POST http://$HOST:$PORT/v1/chat/completions \\"
print_status "    -H 'Content-Type: application/json' \\"
print_status "    -d '{\"messages\": [{\"role\": \"user\", \"content\": \"Xin chào!\"}]}'"
print_status ""
print_status "Press Ctrl+C to stop the server"
print_status "="*60

# Run the server
if python src/qwen_finetune/serving/vllm_server.py; then
    print_success "Server stopped gracefully."
else
    print_error "Server encountered an error."
    print_status "Common issues:"
    print_status "  - CUDA out of memory (reduce gpu_memory_utilization in config)"
    print_status "  - Model loading failed (check model path and format)"
    print_status "  - Port already in use (change port in config)"
    print_status "  - Missing vLLM dependencies (run: pip install vllm)"
    exit 1
fi