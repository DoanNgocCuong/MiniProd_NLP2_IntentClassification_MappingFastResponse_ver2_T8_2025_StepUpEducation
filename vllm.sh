# =============================================================================
# 🚀 VLLM CONFIG CHI TIẾT - QWEN 2.5-1.5B OPTIMIZATION
# =============================================================================

# 🎯 GPU Selection: Chỉ dùng GPU 2 (có ~24GB trống)
# Ví dụ: GPU 0 (98% full), GPU 1 (65% used) → Chọn GPU 2 (2.5% used)

# 💾 Mount HuggingFace cache để không download lại model
# 🌐 Port mapping: Host:30005 → Container:8000  
# 🔗 Shared memory cho multi-processing
# 📦 Container version: v0.4.2 (compatible với CUDA 12.1)

# 🤖 Model: 1.5B parameters - Memory footprint: ~3GB (FP16/BF16)
# 🔐 API authentication key

# 🧠 GPU Memory Usage: 32% của available memory (conservative)
# Ví dụ: GPU có 24GB → vLLM dùng tối đa 7.7GB
# 0.3 = 7.2GB, 0.5 = 12GB, 0.8 = 19.2GB, 0.9 = 21.6GB
# Trade-off: Thấp hơn = an toàn hơn nhưng underutilize GPU

# 📏 Max Sequence Length: 2048 tokens
# KV Cache memory = seq_len × hidden_size × layers × 2 × batch  
# Ví dụ Qwen-1.5B: 2048 × 1536 × 28 × 2 × 16 = ~2.8GB
# 1024→~1.4GB | 2048→~2.8GB | 4096→~5.6GB | 8192→~11.2GB

# 👥 Max Concurrent Requests: 16 requests đồng thời
# Memory per request = KV_cache_size / max_num_seqs
# 8 requests→350MB/req | 16 requests→175MB/req | 32 requests→87MB/req

# 🧱 KV Cache Block Size: 16 tokens/block
# Memory allocation unit = block_size × hidden_size × layers × 2
# 8→0.7MB/block | 16→1.4MB/block | 32→2.8MB/block

# 💿 CPU RAM Backup: 4GB CPU RAM cho overflow KV cache
# 0GB=no backup (risk OOM) | 4GB=moderate | 8GB=safe nhưng chậm khi swap

docker run --runtime nvidia --gpus '"device=1"' \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 30005:8000 \
    --ipc=host \
    vllm/vllm-openai:v0.4.2 \
    --model Qwen/Qwen2.5-1.5B-Instruct \
    --api-key hoailb-vllm \
    --gpu-memory-utilization 0.7 \
    --max-model-len 1024 \
    --max-num-seqs 16 \
    --block-size 16 \
    --swap-space 4

# =============================================================================
# 📊 MEMORY BREAKDOWN SUMMARY:
# Model weights:     ~3.0GB  (Qwen-1.5B FP16)
# KV Cache:          ~2.8GB  (2048 tokens × 16 seqs)  
# Activations:       ~0.5GB  (processing overhead)
# Buffer & CUDA:     ~0.7GB  (vLLM + PyTorch overhead)
# Total GPU VRAM:    ~7.0GB  (với safety margin)
# =============================================================================