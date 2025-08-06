#!/usr/bin/env python3
"""
vLLM serving server for fine-tuned Qwen models
Provides OpenAI-compatible API for chat completions

Author: StepUp Education Team
Date: 2025
"""

import asyncio
import json
import yaml
import time
from typing import List, Dict, Optional, AsyncGenerator
from dataclasses import dataclass
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from vllm import AsyncLLMEngine, AsyncEngineArgs, SamplingParams
from vllm.utils import random_uuid
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ServingConfig:
    """Configuration for vLLM serving"""
    
    # Model configuration
    model_path: str = "models/merged"
    trust_remote_code: bool = True
    
    # Server configuration  
    host: str = "0.0.0.0"
    port: int = 8000
    
    # vLLM engine parameters
    tensor_parallel_size: int = 1
    gpu_memory_utilization: float = 0.9
    max_model_len: int = 2048
    dtype: str = "auto"
    quantization: Optional[str] = None
    max_num_seqs: int = 256
    max_num_batched_tokens: int = 2048
    enforce_eager: bool = False
    
    # Sampling defaults
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 20
    max_tokens: int = 512
    
    # API configuration
    api_key: Optional[str] = None
    cors_allow_origins: List[str] = None


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Chat completion request model"""
    messages: List[ChatMessage] = Field(..., description="List of messages")
    model: Optional[str] = Field(None, description="Model name (ignored)")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperature for sampling")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p for sampling")
    top_k: Optional[int] = Field(None, ge=1, description="Top-k for sampling")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum tokens to generate")
    stream: bool = Field(False, description="Whether to stream the response")
    stop: Optional[List[str]] = Field(None, description="Stop sequences")
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Frequency penalty")


class ChatResponse(BaseModel):
    """Chat completion response model"""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict]
    usage: Dict


class ChatStreamResponse(BaseModel):
    """Chat completion stream response model"""
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[Dict]


class QwenVLLMServer:
    """vLLM server for Qwen models with OpenAI-compatible API"""
    
    def __init__(self, config: ServingConfig):
        self.config = config
        self.engine = None
        self.app = FastAPI(
            title="Qwen vLLM Server",
            description="OpenAI-compatible API for fine-tuned Qwen models",
            version="1.0.0"
        )
        
        # Setup CORS
        cors_origins = config.cors_allow_origins or ["*"]
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self.setup_routes()
        
    async def initialize_engine(self):
        """Initialize vLLM async engine"""
        logger.info("Initializing vLLM engine...")
        logger.info(f"Model path: {self.config.model_path}")
        logger.info(f"GPU memory utilization: {self.config.gpu_memory_utilization}")
        logger.info(f"Max model length: {self.config.max_model_len}")
        logger.info(f"Tensor parallel size: {self.config.tensor_parallel_size}")
        
        try:
            engine_args = AsyncEngineArgs(
                model=self.config.model_path,
                tensor_parallel_size=self.config.tensor_parallel_size,
                gpu_memory_utilization=self.config.gpu_memory_utilization,
                max_model_len=self.config.max_model_len,
                dtype=self.config.dtype,
                quantization=self.config.quantization,
                max_num_seqs=self.config.max_num_seqs,
                max_num_batched_tokens=self.config.max_num_batched_tokens,
                trust_remote_code=self.config.trust_remote_code,
                enforce_eager=self.config.enforce_eager,
            )
            
            self.engine = AsyncLLMEngine.from_engine_args(engine_args)
            logger.info("✅ vLLM engine initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize vLLM engine: {e}")
            raise
        
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.on_event("startup")
        async def startup_event():
            await self.initialize_engine()
            
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            if self.engine is None:
                raise HTTPException(status_code=503, detail="Engine not initialized")
            return {
                "status": "healthy",
                "model_path": self.config.model_path,
                "timestamp": time.time()
            }
            
        @self.app.get("/v1/models")
        async def list_models():
            """List available models (OpenAI compatibility)"""
            return {
                "object": "list",
                "data": [{
                    "id": "qwen-finetuned",
                    "object": "model",
                    "created": int(time.time()),
                    "owned_by": "stepup-education"
                }]
            }
            
        @self.app.post("/v1/chat/completions")
        async def chat_completions(request: ChatRequest, http_request: Request):
            """Chat completions endpoint (OpenAI compatibility)"""
            
            # API key validation if configured
            if self.config.api_key:
                auth_header = http_request.headers.get("authorization")
                if not auth_header or not auth_header.startswith("Bearer "):
                    raise HTTPException(status_code=401, detail="Missing or invalid API key")
                
                provided_key = auth_header.split(" ")[1]
                if provided_key != self.config.api_key:
                    raise HTTPException(status_code=401, detail="Invalid API key")
            
            if request.stream:
                return StreamingResponse(
                    self.handle_chat_stream(request),
                    media_type="text/plain"
                )
            else:
                return await self.handle_chat_request(request)
                
    async def handle_chat_request(self, request: ChatRequest) -> ChatResponse:
        """Handle non-streaming chat completion request"""
        try:
            # Format messages to prompt
            prompt = self.format_messages_to_chatml(request.messages)
            logger.info(f"Generated prompt: {prompt[:200]}...")
            
            # Create sampling parameters
            sampling_params = SamplingParams(
                temperature=request.temperature or self.config.temperature,
                top_p=request.top_p or self.config.top_p,
                top_k=request.top_k or self.config.top_k,
                max_tokens=request.max_tokens or self.config.max_tokens,
                stop=request.stop,
                presence_penalty=request.presence_penalty or 0.0,
                frequency_penalty=request.frequency_penalty or 0.0,
            )
            
            # Generate response
            request_id = random_uuid()
            results = self.engine.generate(prompt, sampling_params, request_id)
            
            # Process results
            final_output = None
            async for request_output in results:
                final_output = request_output
                
            if final_output is None:
                raise HTTPException(status_code=500, detail="Generation failed")
                
            # Create response
            response = ChatResponse(
                id=request_id,
                created=int(time.time()),
                model="qwen-finetuned",
                choices=[{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": final_output.outputs[0].text.strip()
                    },
                    "finish_reason": final_output.outputs[0].finish_reason
                }],
                usage={
                    "prompt_tokens": len(final_output.prompt_token_ids),
                    "completion_tokens": len(final_output.outputs[0].token_ids),
                    "total_tokens": len(final_output.prompt_token_ids) + len(final_output.outputs[0].token_ids)
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling chat request: {e}")
            raise HTTPException(status_code=500, detail=str(e))
            
    async def handle_chat_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Handle streaming chat completion request"""
        try:
            # Format messages to prompt
            prompt = self.format_messages_to_chatml(request.messages)
            
            # Create sampling parameters
            sampling_params = SamplingParams(
                temperature=request.temperature or self.config.temperature,
                top_p=request.top_p or self.config.top_p,
                top_k=request.top_k or self.config.top_k,
                max_tokens=request.max_tokens or self.config.max_tokens,
                stop=request.stop,
                presence_penalty=request.presence_penalty or 0.0,
                frequency_penalty=request.frequency_penalty or 0.0,
            )
            
            # Generate streaming response
            request_id = random_uuid()
            results = self.engine.generate(prompt, sampling_params, request_id)
            
            previous_text = ""
            async for request_output in results:
                if request_output.outputs:
                    current_text = request_output.outputs[0].text
                    new_text = current_text[len(previous_text):]
                    
                    if new_text:
                        chunk = ChatStreamResponse(
                            id=request_id,
                            created=int(time.time()),
                            model="qwen-finetuned",
                            choices=[{
                                "index": 0,
                                "delta": {
                                    "content": new_text
                                },
                                "finish_reason": None
                            }]
                        )
                        yield f"data: {chunk.model_dump_json()}\n\n"
                        previous_text = current_text
            
            # Send final chunk
            final_chunk = ChatStreamResponse(
                id=request_id,
                created=int(time.time()),
                model="qwen-finetuned",
                choices=[{
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop"
                }]
            )
            yield f"data: {final_chunk.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            error_chunk = {
                "error": {
                    "message": str(e),
                    "type": "server_error"
                }
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            
    def format_messages_to_chatml(self, messages: List[ChatMessage]) -> str:
        """Format messages to ChatML prompt format"""
        prompt = ""
        
        for message in messages:
            role = message.role.lower()
            if role not in ["system", "user", "assistant"]:
                role = "user"  # Default fallback
                
            prompt += f"<|im_start|>{role}\n{message.content}<|im_end|>\n"
        
        # Add assistant start token for generation
        prompt += "<|im_start|>assistant\n"
        
        return prompt
        
    def run(self):
        """Run the vLLM server"""
        logger.info(f"🚀 Starting Qwen vLLM server on {self.config.host}:{self.config.port}")
        logger.info(f"Model: {self.config.model_path}")
        logger.info(f"API docs will be available at: http://{self.config.host}:{self.config.port}/docs")
        
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info",
            access_log=True
        )


def load_serving_config(config_path: str) -> ServingConfig:
    """Load serving configuration from YAML file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
            
        config_dict = config_dict or {}
        logger.info(f"Serving configuration loaded from: {config_path}")
        return ServingConfig(**config_dict)
        
    except Exception as e:
        logger.error(f"Error loading serving config: {e}")
        raise


def main():
    """Main serving function"""
    try:
        # Load configuration
        config_path = "configs/serving_config.yaml"
        if not os.path.exists(config_path):
            logger.warning(f"Config file {config_path} not found, using defaults")
            config = ServingConfig()
        else:
            config = load_serving_config(config_path)
        
        # Create and run server
        server = QwenVLLMServer(config)
        server.run()
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    import os
    main()