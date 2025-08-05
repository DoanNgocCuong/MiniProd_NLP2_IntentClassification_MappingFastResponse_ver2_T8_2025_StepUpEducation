# Backup option với v0.7.0
docker run --runtime nvidia --gpus '"device=1"' \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -v $(pwd)/tuning:/workspace/tuning \
    -p 30005:8000 \
    --ipc=host \
    vastai/vllm:v0.7.0-cuda-12.1-pytorch-2.5.1-py312 \
    --model /workspace/tuning/pretrained_models/exported_full_model \
    --api-key hoailb-vllm \
    --gpu-memory-utilization 0.7 \
    --max-model-len 1024 \
    --max-num-seqs 16 \
    --block-size 16 \
    --swap-space 4