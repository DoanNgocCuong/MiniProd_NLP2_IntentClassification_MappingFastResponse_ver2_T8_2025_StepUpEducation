# Em deploy model bằng vllm và đang gặp vấn đề xung đột phiên bản như này ạ. Các anh đã gặp lỗi xung đột này bao giờ chưa ạ. Anh  @Đinh Hùng  , anh  @Hoài Lê Bá  , anh  @Truc Le Van   cứu em với ạ T_T

# Em đang thử tìm các version vllm hỗ trợ Qwen3 và CUDA version 12.1 .... Nhưng chưa fix được ạ. 
# vllm/vllm-openai chỉ chỗ trợ Qwen3 từ v6. 
```
docker run --runtime nvidia --gpus 'device=1' \
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

- Với vllm/vllm-openai:v0.4.2 thì không hõ trợ Qwen3. 
=> tăng version của vllm/vllm-openai:v0.4.2 lên v6, 7, 8, ....Nhưng: 

# Khi version của vllm/vllm-openai tăng lên thì lại yêu cầu CUDA Version >= 12.4  (TRONG KHI CUDA VERSION HIỆN TẠI 12.1)

---
