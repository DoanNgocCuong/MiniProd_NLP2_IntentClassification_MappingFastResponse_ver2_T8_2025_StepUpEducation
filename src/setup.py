"""
Setup script for Qwen Fine-tuning Toolkit
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "Fine-tuning toolkit for Qwen models with vLLM and LoRA"

setup(
    name="qwen-finetune",
    version="0.1.0",
    description="Fine-tuning toolkit for Qwen models with vLLM, LoRA, and Unsloth",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="StepUp Education Team",
    author_email="ai@stepupeducation.vn",
    url="https://github.com/stepupeducation/qwen-finetune",
    packages=find_packages(),
    
    # Core dependencies
    install_requires=[
        # PyTorch ecosystem
        "torch>=2.0.0",
        "transformers>=4.40.0",
        "datasets>=2.18.0",
        "accelerate>=0.28.0",
        "peft>=0.10.0",
        "trl>=0.8.0",
        
        # vLLM for serving
        "vllm>=0.4.0",
        
        # Web framework
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.22.0",
        "pydantic>=2.0.0",
        
        # Utilities
        "pyyaml>=6.0",
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        
        # Optional monitoring
        "wandb>=0.15.0",
    ],
    
    # Extra dependencies for different use cases
    extras_require={
        "unsloth": [
            "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git ; python_version<'3.13'",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipywidgets>=8.0.0",
        ],
        "core": [
            # Core dependencies without unsloth for Python 3.13+
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
            "jupyter>=1.0.0",
            "ipywidgets>=8.0.0",
        ],
        "all": [
            "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git ; python_version<'3.13'",
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
            "jupyter>=1.0.0",
            "ipywidgets>=8.0.0",
        ]
    },
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Entry points for CLI commands
    entry_points={
        "console_scripts": [
            "qwen-train=qwen_finetune.training.finetune_unsloth_chatml:main",
            "qwen-serve=qwen_finetune.serving.vllm_server:main",
            "qwen-process-data=qwen_finetune.utils.data_processor:main",
        ],
    },
    
    # Package classification
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Keywords for PyPI
    keywords=[
        "qwen", "llm", "fine-tuning", "lora", "vllm", "unsloth",
        "chatbot", "language-model", "ai", "machine-learning"
    ],
    
    # Include additional files
    include_package_data=True,
    zip_safe=False,
)