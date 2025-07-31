docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 9090:8000 \
    --ipc=host \
    vllm/vllm-openai:latest \
    vllm --model Qwen/Qwen2.5-1.5B-Instruct --api-keys hoailb-vllm