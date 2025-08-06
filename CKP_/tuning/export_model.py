#!/usr/bin/env python3
"""
Export trained LoRA model to full model format for vLLM deployment
"""

from unsloth import FastLanguageModel
import torch
import os

# Configuration
MODEL_NAME = "unsloth/Qwen3-1.7B"
CHECKPOINT_PATH = "./pretrained_models/unsloth_chatml_finetuned/checkpoint-62"
OUTPUT_PATH = "./pretrained_models/exported_full_model"
max_seq_length = 2048

def export_model():
    """Export LoRA checkpoint to full model format"""
    print(f"Loading trained model from checkpoint: {CHECKPOINT_PATH}")
    
    # Load the trained model directly from checkpoint
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=CHECKPOINT_PATH,  # Load from checkpoint path
        max_seq_length=max_seq_length,
        dtype=None,
        load_in_4bit=False,
    )
    
    # Merge LoRA weights and convert to standard format
    print("Merging LoRA weights into base model...")
    model = FastLanguageModel.for_inference(model)  # This merges LoRA weights
    
    # Save merged model in HuggingFace format
    print(f"Saving full model to: {OUTPUT_PATH}")
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    
    # Save with HuggingFace format (includes config.json)
    model.save_pretrained(OUTPUT_PATH, safe_serialization=True)
    tokenizer.save_pretrained(OUTPUT_PATH)
    
    print("✅ Model export completed!")
    print(f"📁 Full model saved at: {OUTPUT_PATH}")
    print(f"🔧 Update vllm.sh to use: /workspace/tuning/{OUTPUT_PATH}")
    
    # Verify config.json exists
    config_path = f"{OUTPUT_PATH}/config.json"
    if os.path.exists(config_path):
        print("✅ config.json created successfully")
    else:
        print("❌ Warning: config.json not found")

if __name__ == "__main__":
    export_model()