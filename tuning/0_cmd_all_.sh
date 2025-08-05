chmod +x build_env.sh
./build_env.sh: docker build -t llm-unsloth:latest .

chmod +x run_env.sh 
./run_env.sh: docker run --gpus '"device=1"' -it --rm --name llm-unsloth -v $(pwd):/workspace -w /workspace llm-unsloth:latest
pip install -r requirements.txt

python finetune_unsloth_chatml.py

sudo rm -rf checkpoint-60