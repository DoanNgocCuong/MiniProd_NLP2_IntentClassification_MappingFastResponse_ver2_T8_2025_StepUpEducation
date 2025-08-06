# 🤖 Qwen Fine-tuning Toolkit

A comprehensive toolkit for fine-tuning **Qwen2.5/Qwen3** models using **Unsloth**, **LoRA**, and **vLLM** for high-performance serving.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🌟 Features

- **🚀 Fast Training**: Powered by Unsloth for 2x faster fine-tuning
- **💾 Memory Efficient**: LoRA (Low-Rank Adaptation) for parameter-efficient training
- **⚡ High-Performance Serving**: vLLM backend for production-ready API
- **🔄 ChatML Support**: Standardized conversation format
- **🐳 Docker Ready**: Complete containerization support
- **📊 Monitoring**: Weights & Biases integration
- **🌍 Vietnamese Optimized**: Special support for Vietnamese language

## 📂 Project Structure

```
├── 📂 src/                          # Core application code
│   ├── 📂 qwen_finetune/            # Main package
│   │   ├── 📂 training/             # Training modules
│   │   │   └── 📄 finetune_unsloth_chatml.py
│   │   ├── 📂 serving/              # Serving modules
│   │   │   └── 📄 vllm_server.py
│   │   ├── 📂 utils/                # Utilities
│   │   │   └── 📄 data_processor.py
│   │   └── 📄 __init__.py
│   └── 📄 setup.py                  # Package definition
│
├── 📂 configs/                      # Configuration files
│   ├── 📄 training_config.yaml      # Training parameters
│   └── 📄 serving_config.yaml       # Serving parameters
│
├── 📂 data/                         # Training data
│   ├── 📄 pika_data.json           # Training conversations
│   └── 📄 chat_template.txt        # ChatML template
│
├── 📂 models/                       # Model artifacts
│   ├── 📂 pretrained/              # Base models
│   └── 📂 merged/                  # Fine-tuned models
│
├── 📂 deployment/                   # Docker & deployment
│   ├── 📄 Dockerfile
│   └── 📄 docker-compose.yml
│
├── 📂 scripts/                      # Automation scripts
│   ├── 📄 train.sh                 # Training script
│   └── 📄 serve.sh                 # Serving script
│
└── 📄 Makefile                      # Project automation
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone and setup
git clone <your-repo>
cd qwen-finetune

# Automatic setup with Python version detection
make setup

# Or manual setup with Python version detection
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh

# Activate environment
source venv/bin/activate
```

### 🐍 Python Version Compatibility

| Python Version | Training Method | Performance | Compatibility |
|----------------|----------------|-------------|---------------|
| **Python 3.8-3.12** | Unsloth + LoRA | 🚀🚀🚀 **Fastest** | ✅ Full support |
| **Python 3.13+** | Standard LoRA | 🚀🚀 **Fast** | ✅ Compatible |

- **Unsloth** (Python <3.13): 2x faster training, optimized memory usage
- **Standard LoRA** (Python 3.13+): Compatible fallback using PyTorch + PEFT

### 2. Install Dependencies

The setup automatically detects your Python version and installs appropriate dependencies:

```bash
# Automatic installation (recommended)
make setup

# Manual installation
pip install -e src/

# For Python <3.13: Install Unsloth
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

# For Python 3.13+: Core dependencies only (no Unsloth needed)
pip install -e "src/[core]"
```

### 3. Prepare Your Data

```bash
# Create sample data for testing
make data

# Or prepare your own data in ChatML format
# See data/pika_data.json for format example
```

### 4. Fine-tune the Model

```bash
# Start training
make train

# Or run directly
python src/qwen_finetune/training/finetune_unsloth_chatml.py
```

### 5. Serve the Model

```bash
# Start serving API
make serve

# Test the API
make test-api
```

## 📚 Detailed Usage

### Training Configuration

Edit `configs/training_config.yaml`:

```yaml
# Model selection
model_name: "unsloth/Qwen2.5-7B-Instruct-bnb-4bit"  # or Qwen2.5-14B, Qwen3

# LoRA settings
r: 16                    # LoRA rank (higher = more parameters)
lora_alpha: 16          # LoRA scaling
target_modules:         # Modules to apply LoRA
  - "q_proj"
  - "k_proj"
  - "v_proj"
  # ... more modules

# Training parameters
per_device_train_batch_size: 2
gradient_accumulation_steps: 4
max_steps: 60           # Increase for real training
learning_rate: 2.0e-4
```

### Data Format

Training data should be in ChatML conversation format:

```json
[
  {
    "conversations": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Xin chào!"},
      {"role": "assistant", "content": "Chào bạn! Tôi có thể giúp gì?"}
    ]
  }
]
```

### API Usage

Once serving is running:

```bash
# Chat completion
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Xin chào! Bạn có khỏe không?"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

**Python SDK:**

```python
import requests

response = requests.post(
    "http://localhost:8000/v1/chat/completions",
    json={
        "messages": [
            {"role": "user", "content": "Hello!"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
)

print(response.json())
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build Docker image
make docker-build

# Run with Docker Compose
make docker-run

# Or manually
docker run -p 8000:8000 --gpus all qwen-finetune:latest
```

### Production Deployment

```bash
# Production-ready build
docker-compose -f deployment/docker-compose.yml up -d

# Scale horizontally
docker-compose up --scale qwen-finetune=3
```

## ⚙️ Configuration

### Training Settings

| Parameter | Description | Recommended |
|-----------|-------------|-------------|
| `model_name` | Base model to fine-tune | `unsloth/Qwen2.5-7B-Instruct-bnb-4bit` |
| `r` | LoRA rank | 16-64 |
| `max_steps` | Training steps | 1000+ for real training |
| `learning_rate` | Learning rate | 1e-4 to 5e-4 |
| `batch_size` | Batch size per device | 1-4 (adjust for GPU memory) |

### Serving Settings

| Parameter | Description | Recommended |
|-----------|-------------|-------------|
| `gpu_memory_utilization` | GPU memory usage | 0.8-0.9 |
| `max_model_len` | Max sequence length | 2048-4096 |
| `tensor_parallel_size` | GPUs for parallel | 1 for single GPU |

## 🛠️ Development

### Available Commands

```bash
# Development workflow
make help              # Show all commands
make setup             # Complete setup
make train             # Fine-tune model
make serve             # Start API server
make test-api          # Test the API
make clean             # Clean up files

# Data management
make data              # Create sample data
make validate-data     # Validate data format
make analyze-data      # Analyze data statistics

# Code quality
make lint              # Run linting
make format            # Format code
make test              # Run tests
```

### Custom Training

1. **Prepare your data** in ChatML format
2. **Update configuration** in `configs/training_config.yaml`
3. **Run training**: `make train`
4. **Test the model**: `make serve` then `make test-api`

### Adding New Features

1. **Training enhancements**: Modify `src/qwen_finetune/training/`
2. **Serving features**: Update `src/qwen_finetune/serving/`
3. **Data processing**: Extend `src/qwen_finetune/utils/`

## 📊 Monitoring

### Weights & Biases Integration

Enable W&B logging in `configs/training_config.yaml`:

```yaml
use_wandb: true
wandb_project: "qwen-finetune"
wandb_run_name: "qwen-vietnamese-v1"
```

### API Monitoring

- **Health check**: `GET /health`
- **Metrics**: Available at `GET /metrics` (if enabled)
- **Logs**: Check with `docker logs qwen-finetune`

## 🚨 Troubleshooting

### Common Issues

**CUDA Out of Memory:**
```bash
# Reduce batch size in training_config.yaml
per_device_train_batch_size: 1
gradient_accumulation_steps: 8

# Or reduce sequence length
max_seq_length: 1024
```

**Model Loading Fails:**
```bash
# Check model path
ls -la models/merged/

# Verify config.json exists
cat models/merged/config.json
```

**API Connection Refused:**
```bash
# Check if server is running
curl http://localhost:8000/health

# Check ports
lsof -i :8000
```

### Performance Optimization

**For Training:**
- Use `bf16` instead of `fp16` on modern GPUs
- Enable gradient checkpointing for memory
- Use larger batch sizes with gradient accumulation

**For Serving:**
- Increase `gpu_memory_utilization` to 0.95
- Use quantization (AWQ/GPTQ) for memory efficiency
- Enable tensor parallelism for multi-GPU

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- **Unsloth**: For ultra-fast LLM training
- **vLLM**: For high-performance serving
- **Hugging Face**: For transformers and datasets
- **Qwen Team**: For the amazing base models

---

**StepUp Education Team** - 2025

For questions and support, please open an issue or contact us at ai@stepupeducation.vn