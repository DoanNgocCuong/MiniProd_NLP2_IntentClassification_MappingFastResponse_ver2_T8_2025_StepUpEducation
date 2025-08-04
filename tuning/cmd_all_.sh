./build_env.sh: docker build -t llm-unsloth:latest .
./run_env.sh: docker run --gpus '"device=1"' -it --rm --name llm-unsloth -v $(pwd):/workspace -w /workspace llm-unsloth:latest
pip install -r requirements.txt

python finetune_unsloth_chatml.py