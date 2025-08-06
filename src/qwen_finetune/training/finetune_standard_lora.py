#!/usr/bin/env python3
"""
Fine-tune Qwen2.5/Qwen3 using standard PyTorch + LoRA (without Unsloth)
Compatible with Python 3.13+ and all CUDA versions

Author: StepUp Education Team
Date: 2025
"""

import os
import json
import yaml
import torch
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
from peft import LoraConfig, get_peft_model, TaskType
import wandb

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class StandardFineTuneConfig:
    """Configuration for standard fine-tuning (Python 3.13+ compatible)"""
    
    # Model configuration
    model_name: str = "Qwen/Qwen2.5-7B-Instruct"
    max_seq_length: int = 2048
    dtype: str = "bfloat16"  # "float16", "bfloat16", "float32"
    load_in_4bit: bool = False  # Requires bitsandbytes
    load_in_8bit: bool = False
    
    # LoRA parameters
    r: int = 16
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ])
    lora_alpha: int = 16
    lora_dropout: float = 0.1
    bias: str = "none"
    task_type: str = "CAUSAL_LM"
    
    # Training parameters
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 8
    warmup_steps: int = 10
    max_steps: int = 100
    learning_rate: float = 2e-4
    fp16: bool = False
    bf16: bool = True
    logging_steps: int = 1
    optim: str = "adamw_torch"
    weight_decay: float = 0.01
    lr_scheduler_type: str = "linear"
    seed: int = 3407
    output_dir: str = "outputs"
    save_steps: int = 50
    
    # Data parameters
    dataset_text_field: str = "text"
    
    # Model saving
    save_model: bool = True
    save_method: str = "lora"  # "lora" or "merged"
    push_to_hub: bool = False
    hub_model_id: str = ""
    hub_token: str = ""
    
    # Wandb configuration
    use_wandb: bool = False
    wandb_project: str = "qwen-finetune-standard"
    wandb_run_name: str = ""


class StandardQwenFineTuner:
    """Standard LoRA fine-tuner for Qwen models (Python 3.13+ compatible)"""
    
    def __init__(self, config: StandardFineTuneConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
        # Set random seeds
        torch.manual_seed(config.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(config.seed)
        
    def load_model_and_tokenizer(self) -> Tuple[Any, Any]:
        """Load model and tokenizer with LoRA configuration"""
        logger.info(f"Loading model: {self.config.model_name}")
        logger.info(f"Max sequence length: {self.config.max_seq_length}")
        
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_name,
                trust_remote_code=True,
                padding_side="right",
            )
            
            # Add pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            # Configure dtype
            torch_dtype = torch.bfloat16 if self.config.dtype == "bfloat16" else torch.float16
            
            # Load model
            model_kwargs = {
                "trust_remote_code": True,
                "torch_dtype": torch_dtype,
                "device_map": "auto",
            }
            
            # Add quantization if specified
            if self.config.load_in_4bit:
                try:
                    from transformers import BitsAndBytesConfig
                    bnb_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4",
                        bnb_4bit_compute_dtype=torch_dtype
                    )
                    model_kwargs["quantization_config"] = bnb_config
                    logger.info("4-bit quantization enabled")
                except ImportError:
                    logger.warning("bitsandbytes not available, disabling quantization")
                    
            elif self.config.load_in_8bit:
                model_kwargs["load_in_8bit"] = True
                logger.info("8-bit quantization enabled")
            
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_name,
                **model_kwargs
            )
            
            # Configure LoRA
            logger.info("Configuring LoRA adapters...")
            peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=self.config.r,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                bias=self.config.bias,
                target_modules=self.config.target_modules,
            )
            
            self.model = get_peft_model(self.model, peft_config)
            self.model.print_trainable_parameters()
            
            logger.info("Model and tokenizer loaded successfully")
            return self.model, self.tokenizer
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
        
    def prepare_dataset(self, data_path: str, template_path: str) -> Dataset:
        """Prepare dataset with ChatML format"""
        logger.info(f"Loading data from: {data_path}")
        
        try:
            # Load training data
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Load chat template
            with open(template_path, 'r', encoding='utf-8') as f:
                chat_template = f.read().strip()
                
            # Set chat template
            self.tokenizer.chat_template = chat_template
            
            def formatting_prompts_func(examples):
                """Format conversations using ChatML template"""
                convos = examples["conversations"]
                texts = []
                
                for convo in convos:
                    try:
                        # Validate conversation structure
                        if not isinstance(convo, list):
                            continue
                            
                        valid_convo = []
                        for turn in convo:
                            if isinstance(turn, dict) and "role" in turn and "content" in turn:
                                role = turn["role"].lower()
                                if role not in ["system", "user", "assistant"]:
                                    role = "user"
                                    
                                valid_convo.append({
                                    "role": role,
                                    "content": str(turn["content"]).strip()
                                })
                        
                        if not valid_convo:
                            continue
                            
                        # Apply chat template
                        text = self.tokenizer.apply_chat_template(
                            valid_convo,
                            tokenize=False,
                            add_generation_prompt=False
                        )
                        texts.append(text)
                        
                    except Exception as e:
                        logger.warning(f"Error processing conversation: {e}")
                        continue
                
                return {"text": texts}
            
            # Create and process dataset
            dataset = Dataset.from_list(data)
            dataset = dataset.map(
                formatting_prompts_func,
                batched=True,
                remove_columns=dataset.column_names,
                desc="Formatting conversations"
            )
            
            # Filter empty texts
            dataset = dataset.filter(lambda x: len(x["text"].strip()) > 0)
            
            logger.info(f"Dataset prepared with {len(dataset)} samples")
            return dataset
            
        except Exception as e:
            logger.error(f"Error preparing dataset: {e}")
            raise
    
    def tokenize_dataset(self, dataset: Dataset) -> Dataset:
        """Tokenize the dataset"""
        logger.info("Tokenizing dataset...")
        
        def tokenize_function(examples):
            # Tokenize texts
            tokenized = self.tokenizer(
                examples["text"],
                truncation=True,
                padding=False,
                max_length=self.config.max_seq_length,
                return_overflowing_tokens=False,
            )
            
            # For causal language modeling, labels are the same as input_ids
            tokenized["labels"] = tokenized["input_ids"].copy()
            
            return tokenized
        
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names,
            desc="Tokenizing dataset"
        )
        
        logger.info(f"Tokenized dataset: {len(tokenized_dataset)} samples")
        return tokenized_dataset
        
    def create_trainer(self, dataset: Dataset) -> Trainer:
        """Create Hugging Face trainer"""
        logger.info("Creating trainer...")
        
        try:
            # Tokenize dataset
            tokenized_dataset = self.tokenize_dataset(dataset)
            
            training_args = TrainingArguments(
                output_dir=self.config.output_dir,
                per_device_train_batch_size=self.config.per_device_train_batch_size,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                warmup_steps=self.config.warmup_steps,
                max_steps=self.config.max_steps,
                learning_rate=self.config.learning_rate,
                fp16=self.config.fp16,
                bf16=self.config.bf16,
                logging_steps=self.config.logging_steps,
                optim=self.config.optim,
                weight_decay=self.config.weight_decay,
                lr_scheduler_type=self.config.lr_scheduler_type,
                seed=self.config.seed,
                save_strategy="steps",
                save_steps=self.config.save_steps,
                logging_first_step=True,
                remove_unused_columns=False,
                dataloader_pin_memory=False,
                report_to="wandb" if self.config.use_wandb else [],
                run_name=self.config.wandb_run_name if self.config.wandb_run_name else None,
            )
            
            # Data collator for language modeling
            data_collator = DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False,  # We're doing causal language modeling
            )
            
            self.trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=tokenized_dataset,
                data_collator=data_collator,
                tokenizer=self.tokenizer,
            )
            
            logger.info("Trainer created successfully")
            return self.trainer
            
        except Exception as e:
            logger.error(f"Error creating trainer: {e}")
            raise
        
    def train(self) -> Dict[str, Any]:
        """Start training"""
        if self.trainer is None:
            raise ValueError("Trainer not initialized. Call create_trainer() first.")
            
        # Initialize wandb if enabled
        if self.config.use_wandb:
            wandb.init(
                project=self.config.wandb_project,
                name=self.config.wandb_run_name,
                config=self.config.__dict__
            )
            
        try:
            logger.info("=" * 50)
            logger.info("STARTING TRAINING (Standard LoRA)")
            logger.info("=" * 50)
            logger.info(f"Model: {self.config.model_name}")
            logger.info(f"Max steps: {self.config.max_steps}")
            logger.info(f"Batch size: {self.config.per_device_train_batch_size}")
            logger.info(f"LoRA r: {self.config.r}")
            logger.info("=" * 50)
            
            # Train the model
            trainer_stats = self.trainer.train()
            
            logger.info("=" * 50)
            logger.info("TRAINING COMPLETED")
            logger.info("=" * 50)
            
            return trainer_stats
            
        except Exception as e:
            logger.error(f"Error during training: {e}")
            raise
        finally:
            if self.config.use_wandb:
                wandb.finish()
        
    def save_model(self) -> None:
        """Save the fine-tuned model"""
        if not self.config.save_model:
            return
            
        logger.info(f"Saving model using method: {self.config.save_method}")
        
        try:
            if self.config.save_method == "lora":
                # Save LoRA adapters only
                save_path = "models/lora_adapters"
                os.makedirs(save_path, exist_ok=True)
                self.model.save_pretrained(save_path)
                self.tokenizer.save_pretrained(save_path)
                logger.info(f"LoRA adapters saved to: {save_path}")
                
            elif self.config.save_method == "merged":
                # Merge LoRA weights and save full model
                save_path = "models/merged"
                os.makedirs(save_path, exist_ok=True)
                
                # Merge and unload LoRA
                merged_model = self.model.merge_and_unload()
                merged_model.save_pretrained(save_path)
                self.tokenizer.save_pretrained(save_path)
                logger.info(f"Merged model saved to: {save_path}")
                
            # Push to hub if configured
            if self.config.push_to_hub and self.config.hub_model_id:
                logger.info(f"Pushing to Hub: {self.config.hub_model_id}")
                self.model.push_to_hub(
                    self.config.hub_model_id,
                    token=self.config.hub_token if self.config.hub_token else None
                )
                
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise


def load_standard_config(config_path: str) -> StandardFineTuneConfig:
    """Load standard configuration from YAML file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f) or {}
        
        # Map from Unsloth config to standard config
        if "model_name" in config_dict:
            # Convert Unsloth model names to standard HF names
            model_name = config_dict["model_name"]
            if "unsloth/" in model_name:
                # Map unsloth models to standard HF models
                model_name = model_name.replace("unsloth/", "")
                if "bnb-4bit" in model_name:
                    model_name = model_name.replace("-bnb-4bit", "")
                    config_dict["load_in_4bit"] = True
                config_dict["model_name"] = model_name
        
        logger.info(f"Standard configuration loaded from: {config_path}")
        return StandardFineTuneConfig(**config_dict)
        
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise


def main():
    """Main training function for standard LoRA"""
    try:
        # Check Python version
        import sys
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        logger.info(f"Running on Python {python_version}")
        
        if sys.version_info >= (3, 13):
            logger.info("✅ Using standard LoRA training (Python 3.13+ compatible)")
        else:
            logger.info("⚠️  Standard LoRA training (Unsloth recommended for Python <3.13)")
        
        # Load configuration
        # Try standard config first, then fall back to regular config
        config_path = "configs/training_config_standard.yaml"
        if not os.path.exists(config_path):
            config_path = "configs/training_config.yaml"
            logger.info("Using regular training config (will adapt for standard LoRA)")
            
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            return
            
        config = load_standard_config(config_path)
        
        # Validate required files
        data_path = "data/pika_data.json"
        template_path = "data/chat_template.txt"
        
        for path in [data_path, template_path]:
            if not os.path.exists(path):
                logger.error(f"Required file not found: {path}")
                return
        
        # Initialize fine-tuner
        logger.info("Initializing standard Qwen fine-tuner...")
        fine_tuner = StandardQwenFineTuner(config)
        
        # Load model and tokenizer
        fine_tuner.load_model_and_tokenizer()
        
        # Prepare dataset
        dataset = fine_tuner.prepare_dataset(data_path, template_path)
        
        if len(dataset) == 0:
            logger.error("No valid training samples found")
            return
        
        # Create trainer
        fine_tuner.create_trainer(dataset)
        
        # Train the model
        fine_tuner.train()
        
        # Save model
        fine_tuner.save_model()
        
        logger.info("🎉 Standard LoRA fine-tuning completed successfully!")
        
    except Exception as e:
        logger.error(f"Standard fine-tuning failed: {e}")
        raise


if __name__ == "__main__":
    main()