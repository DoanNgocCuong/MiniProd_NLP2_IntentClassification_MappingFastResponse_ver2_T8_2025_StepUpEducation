"""
Qwen Fine-tuning Toolkit
========================

A comprehensive toolkit for fine-tuning Qwen2.5/Qwen3 models using:
- Unsloth for efficient training
- LoRA for parameter-efficient fine-tuning  
- vLLM for high-performance serving
- ChatML format support

Author: StepUp Education Team
Version: 0.1.0
"""

__version__ = "0.1.0"
__author__ = "StepUp Education Team"

from .training.finetune_unsloth_chatml import QwenFineTuner, FineTuneConfig
from .serving.vllm_server import QwenVLLMServer, ServingConfig
from .utils.data_processor import DataProcessor

__all__ = [
    "QwenFineTuner",
    "FineTuneConfig", 
    "QwenVLLMServer",
    "ServingConfig",
    "DataProcessor"
]