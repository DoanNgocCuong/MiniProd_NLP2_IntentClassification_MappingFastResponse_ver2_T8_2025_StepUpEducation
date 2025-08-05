# Vấn đề xung đột phiên bản. 

# Em đang làm 1 bài finetune model: Qwen3-1.7B và host bằng vllm. 

# Vấn đề 1: vllm/vllm-openai chỉ chỗ trợ Qwen3 từ  vllm/vllm-openai:v6. 

```
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
```

Với vllm/vllm-openai:v0.4.2 thì không hõ trợ Qwen3. 

=> tăng version của vllm/vllm-openai:v0.4.2 lên ver 6, ....8, .9, .10 
Nhưng: 

# Vấn đề 2: Khi version của vllm/vllm-openai tăng lên thì lại yêu cầu cấu hình card từ 12.1 (hiện tại) chuyển lên thành >= 12.4 

Mà vấn đề chuyển cấu hình card từ 12.1 lên 12.4 thì ??? Có chuyển được không ạ? 
---


# Ngồi 1h rưỡi không fix được bug version, T_T