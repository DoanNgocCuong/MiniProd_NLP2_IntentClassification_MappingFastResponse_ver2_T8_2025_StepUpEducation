# 🚀 vLLM API - Curl Commands Reference

## 📋 Server Configuration
- **Port**: 30005
- **API Key**: hoailb-vllm
- **Model**: Qwen/Qwen2.5-1.5B-Instruct
- **Max Tokens**: 1024
- **Max Concurrent Requests**: 16

---

## 🔥 Test API cơ bản (Health check)
```bash
curl http://localhost:30005/health
```

---

## 💬 Chat Completion (Khuyến nghị - giống ChatGPT)
```bash
curl -X POST "http://localhost:30005/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hoailb-vllm" \
  -d '{
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
    "messages": [
      {"role": "user", "content": "Xin chào! Bạn có thể giúp tôi không?"}
    ],
    "max_tokens": 512,
    "temperature": 0.7
  }'
```

---

## 📝 Text Completion (Đơn giản hơn)
```bash
curl -X POST "http://localhost:30005/v1/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hoailb-vllm" \
  -d '{
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
    "prompt": "Viết một bài thơ ngắn về mùa thu:",
    "max_tokens": 256,
    "temperature": 0.8
  }'
```

---

## 📋 Liệt kê models có sẵn
```bash
curl -H "Authorization: Bearer hoailb-vllm" \
  http://localhost:30005/v1/models
```

---

## 🎮 Test streaming response (real-time)
```bash
curl -X POST "http://localhost:30005/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hoailb-vllm" \
  -d '{
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
    "messages": [
      {"role": "user", "content": "Giải thích về AI trong 3 câu"}
    ],
    "max_tokens": 200,
    "stream": true
  }' --no-buffer
```

---

## 🔧 Parameters quan trọng

| Parameter | Range | Description |
|-----------|-------|-------------|
| `temperature` | 0.0-2.0 | Càng cao càng creative |
| `max_tokens` | 1-1024 | Số token tối đa (theo config) |
| `top_p` | 0.0-1.0 | Nucleus sampling |
| `frequency_penalty` | -2.0 to 2.0 | Tránh lặp từ |
| `presence_penalty` | -2.0 to 2.0 | Khuyến khích chủ đề mới |

---

## 🎯 Quick Test Commands

### Test 1: Basic Health Check
```bash
curl http://localhost:30005/health
```

### Test 2: Simple Question
```bash
curl -X POST "http://localhost:30005/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hoailb-vllm" \
  -d '{
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
    "messages": [{"role": "user", "content": "Hello, what is 2+2?"}],
    "max_tokens": 100
  }'
```

### Test 3: Vietnamese Language
```bash
curl -X POST "http://localhost:30005/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer hoailb-vllm" \
  -d '{
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
    "messages": [{"role": "user", "content": "Việt Nam có bao nhiêu tỉnh thành?"}],
    "max_tokens": 200,
    "temperature": 0.3
  }'
```

---

## 📊 Expected Response Format

### Chat Completion Response:
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "Qwen/Qwen2.5-1.5B-Instruct",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Response text here..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

---

## ⚠️ Troubleshooting

1. **Connection refused**: Kiểm tra container có đang chạy không
2. **401 Unauthorized**: Kiểm tra API key `hoailb-vllm`
3. **404 Not Found**: Kiểm tra endpoint URL
4. **500 Internal Error**: Kiểm tra logs container
5. **Timeout**: Có thể model đang load, đợi 1-2 phút

### Check container status:
```bash
docker ps | grep vllm
```

### Check logs:
```bash
docker logs <container_id>
```

---

*Generated on: $(date)*
*Server: vLLM v0.4.2 with Qwen2.5-1.5B-Instruct*