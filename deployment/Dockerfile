# Qwen Fine-tuning Toolkit Docker Image
# StepUp Education Team - 2025

FROM nvidia/cuda:11.8-devel-ubuntu22.04

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONPATH="/app/src"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    wget \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create symbolic link for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Upgrade pip
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements first for better caching
COPY src/setup.py ./src/
RUN pip3 install --no-cache-dir -e "src/[all]"

# Copy project files
COPY src/ ./src/
COPY configs/ ./configs/
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY Makefile ./

# Create necessary directories
RUN mkdir -p models/merged models/pretrained outputs

# Set permissions for scripts
RUN chmod +x scripts/*.sh

# Install the package
RUN pip3 install --no-cache-dir -e src/

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Default command - start serving
CMD ["python3", "src/qwen_finetune/serving/vllm_server.py"]

# Alternative entrypoints:
# Training: CMD ["python3", "src/qwen_finetune/training/finetune_unsloth_chatml.py"]
# Data processing: CMD ["python3", "src/qwen_finetune/utils/data_processor.py"]