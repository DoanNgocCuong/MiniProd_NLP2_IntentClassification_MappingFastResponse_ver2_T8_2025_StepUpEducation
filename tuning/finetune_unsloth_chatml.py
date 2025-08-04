from unsloth import FastLanguageModel
import torch
import os 
from unsloth.chat_templates import get_chat_template
from datasets import load_dataset, DatasetDict
from trl import SFTConfig, SFTTrainer

max_seq_length = 2048 
lora_rank = 16 
dtype = None
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
MODEL_NAME = "unsloth/Qwen3-1.7B"
PATH_CHAT_TEMPLATE = "/workspace/chat_template.txt"
PATH_DATASET = "/workspace/dataset/pika_data.json"

def create_dataset(path_dataset, tokenizer):
    
    def formatting_prompts_func(examples):
        texts = [tokenizer.apply_chat_template(conv + [{"role": "assistant", "content": examples["assistant_fast_response"][id]}], tokenize=False, add_generation_prompt=False)
                for id,conv in enumerate(examples["previous_conversation"])]
        return {"text": texts}
    
    dataset = load_dataset("json", data_files=path_dataset, split="train")
    dataset = dataset.map(formatting_prompts_func, batched=True)
    return dataset


def load_models(model_name: str, max_seq_length: int, dtype: torch.dtype = None):

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = model_name,
        max_seq_length = max_seq_length,
        dtype = dtype,
        load_in_4bit = False, # False for LoRA 16bit

    )

    model = FastLanguageModel.get_peft_model(
        model,
        r = 16, # Choose any number > 0 ! Suggested 8, 16, 32, 64, 128
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj",],
        lora_alpha = 16,
        lora_dropout = 0, # Supports any, but = 0 is optimized
        bias = "none",    # Supports any, but = "none" is optimized
        use_gradient_checkpointing = "unsloth", # True or "unsloth" for very long context
        random_state = 3407,
        use_rslora = False,  # We support rank stabilized LoRA
        loftq_config = None, # And LoftQ
    )
    return model, tokenizer

if __name__ == "__main__":
    model, tokenizer = load_models(MODEL_NAME, max_seq_length, dtype)
    chat_template = """"""
    with open("/workspace/chat_template.txt", "r") as f:
        chat_template = f.read()

    tokenizer.chat_template = chat_template


    dataset = create_dataset(
        path_dataset = PATH_DATASET,
        tokenizer = tokenizer,
    )

    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        eval_dataset = None, # Can set up evaluation!,
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        dataset_num_proc = 2,
        args = SFTConfig(
            per_device_train_batch_size = 1,
            gradient_accumulation_steps = 1,
            # Use num_train_epochs = 1, warmup_ratio for full training runs!
            warmup_steps = 5,
            max_steps = 60,
            learning_rate = 2e-4,
            logging_steps = 1,
            optim = "adamw_8bit",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            report_to = "none", # Use this for WandB etc
            output_dir="./pretrained_models/unsloth_chatml_finetuned",
            save_strategy = "steps",
            save_steps = 1000,
        ),
    )

    trainer_stats = trainer.train()
