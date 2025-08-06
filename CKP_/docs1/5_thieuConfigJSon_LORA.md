## 🤔 **Tại sao thiếu config.json?**

Vấn đề này xuất phát từ **cách Unsloth save checkpoint** và **cách vLLM load model**:

### **🔍 Root cause:**

1. **Unsloth checkpoint** chỉ lưu **LoRA adapter weights**, không lưu full model config
2. **vLLM cần full model** với đầy đủ files: `config.json`, `tokenizer.json`, etc.
3. **Export script bạn viết** có vấn đề ở việc load từ checkpoint

---

## 🛠️ **Fix export script:**

Vấn đề ở đây:

```python
# ❌ WRONG: Load từ checkpoint (chỉ có LoRA weights)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=CHECKPOINT_PATH,  # checkpoint-62 chỉ có LoRA
    ...
)
```

**✅ CORRECT approach:**

```python
#!/usr/bin/env python3
"""
Fixed export script - Load base model + apply LoRA checkpoint
"""

from unsloth import FastLanguageModel
from peft import PeftModel
import torch
import os

# Configuration
MODEL_NAME = "unsloth/Qwen3-1.7B"
CHECKPOINT_PATH = "./pretrained_models/unsloth_chatml_finetuned/checkpoint-62"
OUTPUT_PATH = "./pretrained_models/exported_full_model"
max_seq_length = 2048

def export_model():
    print("🔄 Loading base model...")
    
    # 1. Load base model (có đầy đủ config)
    base_model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,  # ✅ Load base model trước
        max_seq_length=max_seq_length,
        dtype=None,
        load_in_4bit=False,
    )
    
    # 2. Apply LoRA weights từ checkpoint
    print("🔄 Applying LoRA checkpoint...")
    model = FastLanguageModel.get_peft_model(
        base_model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                       "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
    )
    
    # 3. Load trained weights từ checkpoint
    print(f"🔄 Loading checkpoint: {CHECKPOINT_PATH}")
    # Cần load state dict từ checkpoint
    checkpoint_files = os.listdir(CHECKPOINT_PATH)
    print(f"📁 Files in checkpoint: {checkpoint_files}")
    
    # Load adapter weights (if exists)
    adapter_path = os.path.join(CHECKPOINT_PATH, "adapter_model.safetensors")
    if os.path.exists(adapter_path):
        from safetensors.torch import load_file
        adapter_weights = load_file(adapter_path)
        model.load_state_dict(adapter_weights, strict=False)
    
    # 4. Merge LoRA và export
    print("🔄 Merging LoRA weights...")
    model = FastLanguageModel.for_inference(model)
    
    # 5. Save merged model
    print(f"💾 Saving to: {OUTPUT_PATH}")
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    
    model.save_pretrained(OUTPUT_PATH, safe_serialization=True)
    tokenizer.save_pretrained(OUTPUT_PATH)
    
    # 6. Verify files
    required_files = ['config.json', 'tokenizer_config.json', 'model.safetensors']
    for file in required_files:
        file_path = os.path.join(OUTPUT_PATH, file)
        if os.path.exists(file_path):
            print(f"✅ {file} - OK")
        else:
            print(f"❌ {file} - MISSING")
    
    print("🎉 Export completed!")

if __name__ == "__main__":
    export_model()
```

---

## 🔧 **Alternative: Sử dụng Unsloth built-in export:**

```python
#!/usr/bin/env python3

from unsloth import FastLanguageModel
import os

MODEL_NAME = "unsloth/Qwen3-1.7B"
LORA_OUTPUT = "./pretrained_models/unsloth_chatml_finetuned"
MERGED_OUTPUT = "./pretrained_models/exported_full_model"

def export_with_unsloth():
    # Load model + LoRA từ thư mục output (không phải checkpoint)
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=LORA_OUTPUT,  # ✅ Load từ thư mục chính, không phải checkpoint
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=False,
    )
    
    # Merge và save
    print("🔄 Merging and saving...")
    model.save_pretrained_merged(
        MERGED_OUTPUT,
        tokenizer,
        save_method="merged_16bit",  # hoặc "merged_4bit" nếu cần
    )
    
    print("✅ Done with Unsloth export!")

if __name__ == "__main__":
    export_with_unsloth()
```

---

## 📊 **Giải thích tại sao xảy ra:**

| Component | Có trong LoRA Checkpoint? | Có trong Base Model? | Cần cho vLLM? |
|-----------|---------------------------|---------------------|---------------|
| `config.json` | ❌ | ✅ | ✅ **Required** |
| `tokenizer.json` | ❌ | ✅ | ✅ **Required** |
| `model weights` | 🔸 Partial (chỉ LoRA) | ✅ Full | ✅ **Full weights** |
| `generation_config.json` | ❌ | ✅ | ✅ **Required** |

**→ Checkpoint chỉ lưu delta weights, không lưu full model config!**

---

## 🎯 **Quick fix - Thử approach này:**

```bash
# 1. Kiểm tra xem có file nào trong checkpoint
ls -la ./pretrained_models/unsloth_chatml_finetuned/

# 2. Nếu có adapter_config.json, sử dụng PEFT merge:
```

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Load base model
base_model = AutoModelForCausalLM.from_pretrained("unsloth/Qwen3-1.7B")
tokenizer = AutoTokenizer.from_pretrained("unsloth/Qwen3-1.7B")

# Load LoRA adapter
model = PeftModel.from_pretrained(
    base_model, 
    "./pretrained_models/unsloth_chatml_finetuned"
)

# Merge
merged_model = model.merge_and_unload()

# Save
merged_model.save_pretrained("./pretrained_models/exported_full_model")
tokenizer.save_pretrained("./pretrained_models/exported_full_model")
```

**Bản chất**: LoRA fine-tune chỉ train adapter weights, cần merge với base model để có full config! 🎯