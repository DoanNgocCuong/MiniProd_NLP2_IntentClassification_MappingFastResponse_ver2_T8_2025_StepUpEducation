#!/usr/bin/env python3
"""
Data processing utilities for Qwen fine-tuning
Handles data format conversion, validation, and sample generation

Author: StepUp Education Team
Date: 2025
"""

import json
import re
import os
from typing import List, Dict, Any, Union, Optional
import logging

logger = logging.getLogger(__name__)


class DataProcessor:
    """Process and validate data for Qwen fine-tuning"""
    
    @staticmethod
    def convert_to_chatml_format(
        input_path: str,
        output_path: str,
        input_format: str = "auto"
    ) -> None:
        """
        Convert various data formats to ChatML conversation format
        
        Args:
            input_path: Path to input data file
            output_path: Path to save converted data
            input_format: Input format ('auto', 'alpaca', 'sharegpt', 'conversations')
        """
        logger.info(f"Converting data from {input_path} to ChatML format")
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                raise ValueError("Input data must be a list")
                
            # Auto-detect format if needed
            if input_format == "auto":
                input_format = DataProcessor._detect_format(data)
                logger.info(f"Detected format: {input_format}")
            
            processed_data = []
            
            for i, item in enumerate(data):
                try:
                    conversations = DataProcessor._convert_item_to_chatml(item, input_format)
                    if conversations:
                        processed_data.append({"conversations": conversations})
                except Exception as e:
                    logger.warning(f"Error processing item {i}: {e}")
                    continue
                    
            # Save processed data
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"✅ Converted {len(processed_data)} samples to {output_path}")
            
        except Exception as e:
            logger.error(f"Error converting data: {e}")
            raise
            
    @staticmethod
    def _detect_format(data: List[Dict]) -> str:
        """Auto-detect data format"""
        if not data:
            return "conversations"
            
        sample = data[0]
        
        if "conversations" in sample:
            return "conversations"
        elif "instruction" in sample:
            return "alpaca"
        elif "from" in sample or "human" in str(sample):
            return "sharegpt"
        else:
            return "conversations"
            
    @staticmethod
    def _convert_item_to_chatml(item: Dict, format_type: str) -> List[Dict]:
        """Convert a single item to ChatML conversation format"""
        conversations = []
        
        if format_type == "conversations":
            if "conversations" in item:
                for turn in item["conversations"]:
                    if isinstance(turn, dict) and "role" in turn and "content" in turn:
                        role = DataProcessor._normalize_role(turn["role"])
                        content = str(turn["content"]).strip()
                        if content:
                            conversations.append({"role": role, "content": content})
                            
        elif format_type == "alpaca":
            # Alpaca format: instruction, input (optional), output
            instruction = item.get("instruction", "").strip()
            input_text = item.get("input", "").strip()
            output = item.get("output", "").strip()
            
            if instruction:
                user_content = instruction
                if input_text:
                    user_content += f"\n\n{input_text}"
                    
                conversations.append({"role": "user", "content": user_content})
                
                if output:
                    conversations.append({"role": "assistant", "content": output})
                    
        elif format_type == "sharegpt":
            # ShareGPT format with "from" and "value" fields
            if isinstance(item, list):
                # Direct conversation list
                conv_list = item
            else:
                # Nested conversation
                conv_list = item.get("conversations", [])
                
            for turn in conv_list:
                if isinstance(turn, dict):
                    role = DataProcessor._normalize_role(turn.get("from", "user"))
                    content = str(turn.get("value", "")).strip()
                    if content:
                        conversations.append({"role": role, "content": content})
                        
        return conversations
        
    @staticmethod
    def _normalize_role(role: str) -> str:
        """Normalize role names to standard format"""
        role = str(role).lower().strip()
        
        if role in ["human", "user"]:
            return "user"
        elif role in ["assistant", "gpt", "bot", "ai"]:
            return "assistant"
        elif role == "system":
            return "system"
        else:
            logger.warning(f"Unknown role '{role}', defaulting to 'user'")
            return "user"
            
    @staticmethod
    def validate_data(data_path: str, strict: bool = False) -> bool:
        """
        Validate ChatML conversation data format
        
        Args:
            data_path: Path to data file
            strict: Whether to use strict validation
            
        Returns:
            bool: True if validation passes
        """
        logger.info(f"Validating data: {data_path}")
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if not isinstance(data, list):
                logger.error("❌ Data must be a list of conversation objects")
                return False
                
            valid_samples = 0
            total_samples = len(data)
            
            for i, item in enumerate(data):
                try:
                    if not DataProcessor._validate_conversation_item(item, strict):
                        if strict:
                            logger.error(f"❌ Validation failed at item {i}")
                            return False
                        else:
                            logger.warning(f"⚠️ Item {i} has validation issues")
                    else:
                        valid_samples += 1
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error validating item {i}: {e}")
                    if strict:
                        return False
                        
            logger.info(f"✅ Validation completed: {valid_samples}/{total_samples} valid samples")
            return valid_samples > 0
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False
            
    @staticmethod
    def _validate_conversation_item(item: Dict, strict: bool = False) -> bool:
        """Validate a single conversation item"""
        if not isinstance(item, dict):
            return False
            
        if "conversations" not in item:
            return False
            
        conversations = item["conversations"]
        if not isinstance(conversations, list) or len(conversations) == 0:
            return False
            
        for turn in conversations:
            if not isinstance(turn, dict):
                return False
                
            if "role" not in turn or "content" not in turn:
                return False
                
            role = str(turn["role"]).strip().lower()
            content = str(turn["content"]).strip()
            
            if not role or not content:
                return False
                
            if strict and role not in ["user", "assistant", "system"]:
                return False
                
        return True
        
    @staticmethod
    def create_sample_data(
        output_path: str,
        num_samples: int = 10,
        language: str = "vi"
    ) -> None:
        """
        Create sample training data for testing
        
        Args:
            output_path: Path to save sample data
            num_samples: Number of sample conversations to create
            language: Language for samples ('vi' or 'en')
        """
        logger.info(f"Creating {num_samples} sample conversations in {language}")
        
        if language == "vi":
            sample_templates = [
                {
                    "user": "Xin chào! Bạn có khỏe không?",
                    "assistant": "Xin chào! Tôi khỏe, cảm ơn bạn đã hỏi. Bạn cần tôi giúp gì không?"
                },
                {
                    "user": "Hãy giải thích về trí tuệ nhân tạo.",
                    "assistant": "Trí tuệ nhân tạo (AI) là khả năng của máy tính thực hiện các tác vụ thường đòi hỏi trí thông minh của con người, như học hỏi, suy luận và giải quyết vấn đề."
                },
                {
                    "user": "Làm thế nào để học lập trình hiệu quả?",
                    "assistant": "Để học lập trình hiệu quả: 1) Bắt đầu với ngôn ngữ phù hợp, 2) Thực hành thường xuyên, 3) Xây dựng dự án thực tế, 4) Đọc code của người khác, 5) Tham gia cộng đồng lập trình."
                },
                {
                    "user": "Bạn có thể viết một bài thơ ngắn không?",
                    "assistant": "Đây là một bài thơ ngắn:\n\nMây trắng trôi trên trời xanh,\nGió nhẹ thổi qua cành lá.\nThời gian như dòng nước chảy,\nCuộc đời đẹp như tranh vẽ."
                },
                {
                    "user": "Tôi đang buồn, bạn có thể an ủi tôi không?",
                    "assistant": "Tôi hiểu bạn đang cảm thấy buồn. Hãy nhớ rằng mọi cảm xúc đều tạm thời, và sau cơn mưa sẽ có cầu vồng. Bạn có muốn chia sẻ điều gì đang làm bạn buồn không?"
                }
            ]
        else:  # English
            sample_templates = [
                {
                    "user": "Hello! How are you doing today?",
                    "assistant": "Hello! I'm doing well, thank you for asking. How can I help you today?"
                },
                {
                    "user": "Can you explain machine learning?",
                    "assistant": "Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms to identify patterns in data and make predictions."
                },
                {
                    "user": "What's the best way to learn programming?",
                    "assistant": "To learn programming effectively: 1) Start with a beginner-friendly language, 2) Practice consistently, 3) Build real projects, 4) Read others' code, 5) Join programming communities and ask questions."
                },
                {
                    "user": "Can you write a short poem?",
                    "assistant": "Here's a short poem for you:\n\nStars shine bright in the night sky,\nDreams take flight, reaching high.\nEvery moment, a chance to grow,\nLet your inner light always glow."
                },
                {
                    "user": "I'm feeling sad, can you cheer me up?",
                    "assistant": "I'm sorry you're feeling sad. Remember that difficult feelings are temporary, and you're stronger than you know. Would you like to talk about what's bothering you, or would you prefer a distraction?"
                }
            ]
        
        sample_data = []
        
        for i in range(num_samples):
            template = sample_templates[i % len(sample_templates)]
            
            conversations = [
                {"role": "user", "content": template["user"]},
                {"role": "assistant", "content": template["assistant"]}
            ]
            
            # Add some variation
            if i % 3 == 0 and language == "vi":
                # Add system message for some samples
                conversations.insert(0, {
                    "role": "system",
                    "content": "Bạn là một trợ lý AI thông minh và hữu ích, luôn trả lời bằng tiếng Việt."
                })
            elif i % 3 == 0 and language == "en":
                conversations.insert(0, {
                    "role": "system", 
                    "content": "You are a helpful and intelligent AI assistant."
                })
            
            sample_data.append({"conversations": conversations})
            
        # Save sample data
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"✅ Created {num_samples} sample conversations in {output_path}")
        
    @staticmethod
    def analyze_data(data_path: str) -> Dict[str, Any]:
        """Analyze conversation data and return statistics"""
        logger.info(f"Analyzing data: {data_path}")
        
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            stats = {
                "total_conversations": len(data),
                "total_turns": 0,
                "roles": {},
                "avg_turns_per_conversation": 0,
                "content_lengths": [],
                "empty_conversations": 0
            }
            
            for conversation in data:
                if "conversations" not in conversation:
                    stats["empty_conversations"] += 1
                    continue
                    
                turns = conversation["conversations"]
                if not turns:
                    stats["empty_conversations"] += 1
                    continue
                    
                stats["total_turns"] += len(turns)
                
                for turn in turns:
                    role = turn.get("role", "unknown")
                    content = turn.get("content", "")
                    
                    stats["roles"][role] = stats["roles"].get(role, 0) + 1
                    stats["content_lengths"].append(len(content))
                    
            if stats["total_conversations"] > 0:
                stats["avg_turns_per_conversation"] = stats["total_turns"] / stats["total_conversations"]
                
            if stats["content_lengths"]:
                stats["avg_content_length"] = sum(stats["content_lengths"]) / len(stats["content_lengths"])
                stats["min_content_length"] = min(stats["content_lengths"])
                stats["max_content_length"] = max(stats["content_lengths"])
            
            logger.info(f"📊 Data Analysis Results:")
            logger.info(f"  Total conversations: {stats['total_conversations']}")
            logger.info(f"  Total turns: {stats['total_turns']}")
            logger.info(f"  Average turns per conversation: {stats['avg_turns_per_conversation']:.2f}")
            logger.info(f"  Role distribution: {stats['roles']}")
            logger.info(f"  Average content length: {stats.get('avg_content_length', 0):.2f} characters")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error analyzing data: {e}")
            raise
            
    @staticmethod
    def split_data(
        input_path: str,
        train_ratio: float = 0.8,
        val_ratio: float = 0.1,
        test_ratio: float = 0.1,
        output_dir: str = "data"
    ) -> None:
        """Split data into train/validation/test sets"""
        logger.info(f"Splitting data from {input_path}")
        
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
            raise ValueError("Ratios must sum to 1.0")
            
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            import random
            random.shuffle(data)
            
            total = len(data)
            train_end = int(total * train_ratio)
            val_end = train_end + int(total * val_ratio)
            
            train_data = data[:train_end]
            val_data = data[train_end:val_end]
            test_data = data[val_end:]
            
            # Save splits
            os.makedirs(output_dir, exist_ok=True)
            
            splits = [
                (train_data, f"{output_dir}/train.json"),
                (val_data, f"{output_dir}/val.json"),
                (test_data, f"{output_dir}/test.json")
            ]
            
            for split_data, split_path in splits:
                with open(split_path, 'w', encoding='utf-8') as f:
                    json.dump(split_data, f, ensure_ascii=False, indent=2)
                    
            logger.info(f"✅ Data split completed:")
            logger.info(f"  Train: {len(train_data)} samples -> {output_dir}/train.json")
            logger.info(f"  Val: {len(val_data)} samples -> {output_dir}/val.json")
            logger.info(f"  Test: {len(test_data)} samples -> {output_dir}/test.json")
            
        except Exception as e:
            logger.error(f"Error splitting data: {e}")
            raise


def main():
    """Test data processor functionality"""
    processor = DataProcessor()
    
    # Create sample data
    processor.create_sample_data("data/pika_data.json", 20, "vi")
    
    # Validate data
    is_valid = processor.validate_data("data/pika_data.json")
    print(f"Data validation: {'PASSED' if is_valid else 'FAILED'}")
    
    # Analyze data
    stats = processor.analyze_data("data/pika_data.json")
    print(f"Analysis completed: {stats}")


if __name__ == "__main__":
    main()