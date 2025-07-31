docker run --runtime nvidia --gpus all \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    -p 23333:23333 \
    --ipc=host \
    openmmlab/lmdeploy:v0.7.2.post1-cu12 \
    lmdeploy serve api_server Qwen/Qwen2.5-1.5B-Instruct --server-port 23333 --cache-max-entry-count 0.9 \
            --api-keys hoailb-vllm 