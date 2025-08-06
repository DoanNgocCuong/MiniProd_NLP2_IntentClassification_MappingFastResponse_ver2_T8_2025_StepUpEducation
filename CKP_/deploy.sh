# python -m vllm.entrypoints.openai.api_server \
#     --model ./merged_qwen3_finetuned \
#     --host 0.0.0.0 \
#     --tensor-parallel-size 1 \
#     --gpu-memory-utilization 0.7 \
#     --max-model-len 1024 


docker run --runtime nvidia --gpus '"device=1"' \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -v $(pwd)/tuning/pretrained_models/exported_full_model:/app/model \
    -p 30005:8000 \
    --ipc=host \
    vllm/vllm-openai:v0.4.2 \
    --model /app/model \
    --api-key hoailb-vllm \
    --gpu-memory-utilization 0.7 \
    --trust-remote-code


# CKP_/merged_qwen3_finetuned/ directory. This could happen because: