Dưới đây là **bảng so sánh cập nhật mới nhất** — tổng hợp hiệu suất, mức dùng VRAM và ưu nhược điểm của 5 framework phổ biến khi inference model **Qwen2.5‑1.5B**:

---

## &#x20;Bảng So Sánh

| Framework                      | VRAM sử dụng (1.5B FP16)                                                                                       | Tốc độ & Throughput                                                                            | API OpenAI ✅   | Ưu điểm chính                                    | Hạn chế chính                                      |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | -------------- | ------------------------------------------------ | -------------------------------------------------- |
| **vLLM**                       | \~15–17 GB (pre-allocate toàn GPU) ([GitHub][1], [GitHub][2])                                                  | TTFT cực thấp, throughput tốt nhưng token/s trung bình ([BentoML][3], [VLLM Documentation][4]) | ✅              | Streaming tốt, hỗ trợ batching, OpenAI API chuẩn | Rất tốn VRAM, cấu hình phức tạp                    |
| **LMDeploy**                   | \~5–7 GB (FP16, blocking KV cache) ([PyPI][5], [GitHub][6])                                                    | Token generation rate cao nhất (\~1.8× vLLM), TTFT tốt ở concurrency cao ([BentoML][3])        | ✅              | throughput cao, tiết kiệm VRAM đáng kể           | Hỗ trợ model mới còn hạn chế                       |
| **Ollama (llama.cpp backend)** | \~2–8 GB (quantized Q4/INT8) ([onedollarvps.com][7], [Ollama][8], [Radxa Docs][9], [ApX Machine Learning][10]) | Thường chậm hơn vLLM/LMDeploy (đặc biệt non-draft)                                             | ✅ (phiên bản)  | Dễ dùng, sử dụng GGUF, khả năng extrapolate tốt  | Không tối ưu throughput, limited concurrency       |
| **llama.cpp**                  | \~3–5 GB (Q4\_K\_M quantized) ([Radxa Docs][9], [ApX Machine Learning][10])                                    | CPU inference hoặc GPU nhẹ, token/s thấp                                                       | ❌ (có wrapper) | Nhẹ, chạy trên CPU hoặc GPU nhỏ giá rẻ           | Chậm, không streaming, API không chuẩn             |
| **Unsloth**                    | Tương đương llama.cpp hoặc Qwen-coder 1.5B quantized \~2–4 GB                                                  | Tốc độ inference chấp nhận được, fine‑tune nhanh                                               | ❌              | Rất nhẹ, fine-tune efficient, tiết kiệm VRAM     | Không tối ưu inference API, ít tính năng streaming |

---

## &#x20;Các nguồn đánh giá đáng tin cậy

* vLLM luôn **pre-allocate toàn bộ GPU memory cho KV cache** nên dù model nhỏ vẫn chiếm VRAM lớn (\~17 GB) — phản ánh qua nhiều issue và tài liệu ([GitHub][2]).
* vLLM benchmarking vs LMDeploy/Triton được xác nhận trong các benchmark độc lập, cho thấy LMDeploy có throughput cao hơn \~1.8×, nhưng vLLM luôn có TTFT thấp hơn ([BentoML][3]).
* LMDeploy giới thiệu các kỹ thuật như **persistent batch, blocked KV cache** giúp tối ưu memory và throughput ([PyPI][5]).
* Ollama (dựa trên llama.cpp) hỗ trợ các mức quantization Q4\_/INT8 giúp giảm VRAM đến \~2–8 GB cho model \~1.5B ([onedollarvps.com][7]).

---

## &#x20;Kết luận theo nhu cầu chính:

* **Nếu muốn throughput và latency tốt, but không quá quan tâm đến VRAM** → **vLLM** là lựa chọn mạnh, streaming tốt.
* **Nếu muốn tiết kiệm VRAM (\~5–7 GB) và vẫn giữ tốc độ cao, hỗ trợ OpenAI API** → chọn **LMDeploy**.
* **Nếu GPU nhỏ, muốn chạy nhẹ trên CPU hoặc dùng quantized models** → **Ollama / llama.cpp** là hợp lý.
* **Nếu cần nhẹ nhất, khả năng fine‑tune tương đối, inference đơn giản** → **Unsloth** hoặc bản llama.cpp.

---

Nếu bạn cần mình giúp viết **script Docker lệnh chạy LMDeploy**, hoặc cấu hình tối ưu cho GPU cụ thể (ví dụ 8 GB VRAM), cứ nói nhé!

[1]: https://github.com/vllm-project/vllm/issues/10360?utm_source=chatgpt.com "[Bug]: v0.6.4 requires more GPU memory than v0.6.3 #10360"
[2]: https://github.com/vllm-project/vllm/issues/4253?utm_source=chatgpt.com "[Usage]: Why 0.5B model requires 21G gpu ram - GitHub"
[3]: https://bentoml.com/blog/benchmarking-llm-inference-backends?utm_source=chatgpt.com "Benchmarking LLM Inference Backends - BentoML"
[4]: https://docs.vllm.ai/en/v0.6.3/performance_benchmark/benchmarks.html?utm_source=chatgpt.com "Benchmark suites of vLLM"
[5]: https://pypi.org/project/lmdeploy/?utm_source=chatgpt.com "lmdeploy - PyPI"
[6]: https://github.com/InternLM/lmdeploy?utm_source=chatgpt.com "GitHub - InternLM/lmdeploy: LMDeploy is a toolkit for compressing ..."
[7]: https://onedollarvps.com/blogs/how-to-run-qwen3-locally?utm_source=chatgpt.com "How to Run Qwen3 Locally - A Practical Guide for AI Enthusiasts"
[8]: https://ollama.com/library/qwen?utm_source=chatgpt.com "qwen - Ollama"
[9]: https://docs.radxa.com/en/orion/o6/app-development/artificial-intelligence/llama_cpp?utm_source=chatgpt.com "Llama.cpp | Radxa Docs"
[10]: https://apxml.com/posts/best-local-llms-for-every-nvidia-rtx-50-series-gpu?utm_source=chatgpt.com "Best Local LLMs for Every NVIDIA RTX 50 Series GPU"
