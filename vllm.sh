docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 30005:8000 \
    --ipc=host \
    vllm/vllm-openai:v0.4.2 \
    --model Qwen/Qwen2.5-1.5B-Instruct --api-key hoailb-vllm 