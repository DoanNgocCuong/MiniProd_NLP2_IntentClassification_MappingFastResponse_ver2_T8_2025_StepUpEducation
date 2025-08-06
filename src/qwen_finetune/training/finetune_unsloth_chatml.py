#!/usr/bin/env python3
"""
Fine-tune Qwen2.5/Qwen3 using Unsloth and LoRA
Support for ChatML format and vLLM serving

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
from transformers import TrainingArguments
from datasets import Dataset, load_dataset
from unsloth import FastLanguageModel, is_bfloat16_supported
from unsloth.chat_templates import get_chat_template
from trl import SFTTrainer
import wandb

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class FineTuneConfig:
    """Configuration for fine-tuning Qwen models"""
    
    # Model configuration
    model_name: str = "unsloth/Qwen2.5-7B-Instruct-bnb-4bit"
    max_seq_length: int = 2048
    dtype: Optional[torch.dtype] = None
    load_in_4bit: bool = True
    
    # LoRA parameters
    r: int = 16
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ])
    lora_alpha: int = 16
    lora_dropout: float = 0.0
    bias: str = "none"
    use_gradient_checkpointing: str = "unsloth"
    random_state: int = 3407
    use_rslora: bool = False
    loftq_config: Optional[Dict] = None
    
    # Training parameters
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 5
    max_steps: int = 60
    learning_rate: float = 2e-4
    fp16: bool = not is_bfloat16_supported()
    bf16: bool = is_bfloat16_supported()
    logging_steps: int = 1
    optim: str = "adamw_8bit"
    weight_decay: float = 0.01
    lr_scheduler_type: str = "linear"
    seed: int = 3407
    output_dir: str = "outputs"
    
    # Data parameters
    dataset_text_field: str = "text"
    packing: bool = False
    
    # Model saving
    save_model: bool = True
    save_method: str = "merged_16bit"  # "lora", "merged_16bit", "merged_4bit"
    push_to_hub: bool = False
    hub_model_id: str = ""
    hub_token: str = ""
    
    # Wandb configuration
    use_wandb: bool = False
    wandb_project: str = "qwen-finetune"
    wandb_run_name: str = ""


class QwenFineTuner:
    """Fine-tuner for Qwen models using Unsloth and LoRA"""
    
    def __init__(self, config: FineTuneConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
        # Set random seeds for reproducibility
        torch.manual_seed(config.seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(config.seed)
        
    def load_model_and_tokenizer(self) -> Tuple[Any, Any]:
        """Load model and tokenizer with LoRA configuration"""
        logger.info(f"Loading model: {self.config.model_name}")
        logger.info(f"Max sequence length: {self.config.max_seq_length}")
        logger.info(f"Load in 4bit: {self.config.load_in_4bit}")
        
        try:
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.config.model_name,
                max_seq_length=self.config.max_seq_length,
                dtype=self.config.dtype,
                load_in_4bit=self.config.load_in_4bit,
            )
            
            # Configure LoRA adapters
            logger.info("Configuring LoRA adapters...")
            logger.info(f"LoRA r: {self.config.r}")
            logger.info(f"LoRA alpha: {self.config.lora_alpha}")
            logger.info(f"Target modules: {self.config.target_modules}")
            
            self.model = FastLanguageModel.get_peft_model(
                self.model,
                r=self.config.r,
                target_modules=self.config.target_modules,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                bias=self.config.bias,
                use_gradient_checkpointing=self.config.use_gradient_checkpointing,
                random_state=self.config.random_state,
                use_rslora=self.config.use_rslora,
                loftq_config=self.config.loftq_config,
            )
            
            logger.info("Model and tokenizer loaded successfully")
            return self.model, self.tokenizer
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
        
    def prepare_dataset(self, data_path: str, template_path: str) -> Dataset:
        """Prepare dataset with ChatML format"""
        logger.info(f"Loading data from: {data_path}")
        logger.info(f"Using template from: {template_path}")
        
        try:
            # Load training data
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("Data must be a list of conversation objects")
                
            logger.info(f"Loaded {len(data)} training examples")
            
            # Load chat template
            with open(template_path, 'r', encoding='utf-8') as f:
                chat_template = f.read().strip()
                
            # Set chat template on tokenizer
            self.tokenizer.chat_template = chat_template
            logger.info("Chat template configured")
            
            def formatting_prompts_func(examples):
                """Format conversations using ChatML template"""
                convos = examples["conversations"]
                texts = []
                
                for convo in convos:
                    try:
                        # Ensure proper conversation format
                        if not isinstance(convo, list):
                            logger.warning(f"Skipping invalid conversation: {convo}")
                            continue
                            
                        # Validate conversation structure
                        valid_convo = []
                        for turn in convo:
                            if isinstance(turn, dict) and "role" in turn and "content" in turn:
                                # Normalize role names
                                role = turn["role"].lower()
                                if role in ["human", "user"]:
                                    role = "user"
                                elif role in ["assistant", "gpt", "bot"]:
                                    role = "assistant"
                                elif role == "system":
                                    role = "system"
                                else:
                                    logger.warning(f"Unknown role: {role}, defaulting to user")
                                    role = "user"
                                    
                                valid_convo.append({
                                    "role": role,
                                    "content": str(turn["content"]).strip()
                                })
                        
                        if not valid_convo:
                            logger.warning("Skipping empty conversation")
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
            original_columns = dataset.column_names
            
            dataset = dataset.map(
                formatting_prompts_func,
                batched=True,
                remove_columns=original_columns,
                desc="Formatting conversations"
            )
            
            # Filter out empty texts
            dataset = dataset.filter(lambda x: len(x["text"].strip()) > 0)
            
            logger.info(f"Dataset prepared with {len(dataset)} valid samples")
            
            # Log a sample for verification
            if len(dataset) > 0:
                logger.info("Sample formatted text:")
                logger.info(dataset[0]["text"][:500] + "..." if len(dataset[0]["text"]) > 500 else dataset[0]["text"])
            
            return dataset
            
        except Exception as e:
            logger.error(f"Error preparing dataset: {e}")
            raise
        
    def create_trainer(self, dataset: Dataset) -> SFTTrainer:
        """Create SFT trainer with optimized settings"""
        logger.info("Creating SFT trainer...")
        
        try:
            training_args = TrainingArguments(
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
                output_dir=self.config.output_dir,
                report_to="wandb" if self.config.use_wandb else [],
                run_name=self.config.wandb_run_name if self.config.wandb_run_name else None,
                save_strategy="steps",
                save_steps=max(self.config.max_steps // 4, 1),
                logging_first_step=True,
                remove_unused_columns=False,
                dataloader_pin_memory=False,
            )
            
            self.trainer = SFTTrainer(
                model=self.model,
                tokenizer=self.tokenizer,
                train_dataset=dataset,
                dataset_text_field=self.config.dataset_text_field,
                max_seq_length=self.config.max_seq_length,
                dataset_num_proc=2,
                packing=self.config.packing,
                args=training_args,
            )
            
            logger.info("SFT trainer created successfully")
            return self.trainer
            
        except Exception as e:
            logger.error(f"Error creating trainer: {e}")
            raise
        
    def train(self) -> Dict[str, Any]:
        """Start the training process"""
        if self.trainer is None:
            raise ValueError("Trainer not initialized. Call create_trainer() first.")
            
        # Initialize wandb if enabled
        if self.config.use_wandb:
            wandb.init(
                project=self.config.wandb_project,
                name=self.config.wandb_run_name,
                config=self.config.__dict__
            )
            logger.info(f"Wandb initialized for project: {self.config.wandb_project}")
            
        try:
            logger.info("=" * 50)
            logger.info("STARTING TRAINING")
            logger.info("=" * 50)
            logger.info(f"Model: {self.config.model_name}")
            logger.info(f"Max steps: {self.config.max_steps}")
            logger.info(f"Batch size: {self.config.per_device_train_batch_size}")
            logger.info(f"Gradient accumulation: {self.config.gradient_accumulation_steps}")
            logger.info(f"Learning rate: {self.config.learning_rate}")
            logger.info(f"LoRA r: {self.config.r}")
            logger.info("=" * 50)
            
            # Train the model
            trainer_stats = self.trainer.train()
            
            logger.info("=" * 50)
            logger.info("TRAINING COMPLETED")
            logger.info("=" * 50)
            logger.info(f"Final loss: {trainer_stats.training_loss:.4f}")
            logger.info(f"Training time: {trainer_stats.metrics.get('train_runtime', 0):.2f} seconds")
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
            logger.info("Model saving disabled")
            return
            
        logger.info(f"Saving model using method: {self.config.save_method}")
        
        try:
            if self.config.save_method == "lora":
                # Save only LoRA adapters
                save_path = "models/lora_adapters"
                os.makedirs(save_path, exist_ok=True)
                self.model.save_pretrained(save_path)
                self.tokenizer.save_pretrained(save_path)
                logger.info(f"LoRA adapters saved to: {save_path}")
                
            elif self.config.save_method in ["merged_16bit", "merged_4bit"]:
                # Save merged model
                save_path = "models/merged"
                os.makedirs(save_path, exist_ok=True)
                self.model.save_pretrained_merged(
                    save_path,
                    self.tokenizer,
                    save_method=self.config.save_method
                )
                logger.info(f"Merged model saved to: {save_path}")
                
            else:
                raise ValueError(f"Unknown save method: {self.config.save_method}")
            
            # Push to Hugging Face Hub if configured
            if self.config.push_to_hub and self.config.hub_model_id:
                logger.info(f"Pushing to Hub: {self.config.hub_model_id}")
                if self.config.save_method == "lora":
                    self.model.push_to_hub(
                        self.config.hub_model_id,
                        token=self.config.hub_token if self.config.hub_token else None
                    )
                else:
                    self.model.push_to_hub_merged(
                        self.config.hub_model_id,
                        self.tokenizer,
                        save_method=self.config.save_method,
                        token=self.config.hub_token if self.config.hub_token else None
                    )
                logger.info("Model pushed to Hub successfully")
                
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise


def load_config(config_path: str) -> FineTuneConfig:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        
        # Handle missing optional fields
        config_dict = config_dict or {}
        
        logger.info(f"Configuration loaded from: {config_path}")
        return FineTuneConfig(**config_dict)
        
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise


def main():
    """Main training function"""
    try:
        # Load configuration
        config_path = "configs/training_config.yaml"
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            return
            
        config = load_config(config_path)
        
        # Validate required files
        data_path = "data/pika_data.json"
        template_path = "data/chat_template.txt"
        
        if not os.path.exists(data_path):
            logger.error(f"Data file not found: {data_path}")
            return
            
        if not os.path.exists(template_path):
            logger.error(f"Template file not found: {template_path}")
            return
        
        # Initialize fine-tuner
        logger.info("Initializing Qwen fine-tuner...")
        fine_tuner = QwenFineTuner(config)
        
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
        
        logger.info("🎉 Fine-tuning process completed successfully!")
        
    except Exception as e:
        logger.error(f"Fine-tuning failed: {e}")
        raise


if __name__ == "__main__":
    main()