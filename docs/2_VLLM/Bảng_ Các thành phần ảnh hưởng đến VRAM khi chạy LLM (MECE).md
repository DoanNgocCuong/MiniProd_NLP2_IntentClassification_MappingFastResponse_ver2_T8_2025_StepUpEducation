## Bảng: Các thành phần ảnh hưởng đến VRAM khi chạy LLM (MECE)

| **Thành phần**                                                                                     | **So với model size (B)**              | **Config ảnh hưởng chính & mô tả chi tiết**                                                                                                                          |
| -------------------------------------------------------------------------------------------------- | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Model Weights**<br>📌 `precision=fp16/int4`                                                      | `= 1.0×` với FP16<br>`~0.25×` với INT4 | **`precision`**: FP16 = 2 bytes/param, INT4 = \~0.5 bytes/param. <br>Giảm precision giúp giảm mạnh VRAM và tăng throughput.                                          |
| **KV Cache**<br>📌 `--max-model-len`, `batch_size`                                                 | `~0.2 – 0.6×`                          | **`--max-model-len`**: sequence length tối đa (4096 token tăng cache ×4 so với 1024).<br>**`batch_size`**: càng lớn → KV Cache càng phình ra.                        |
| **Activation Memory**<br>📌 `batch_size`, `model depth`                                            | `~0.2 – 0.4×`                          | **`batch_size`**: ảnh hưởng mạnh đến memory intermediate.<br>**`model depth`**: càng nhiều layers → tăng memory theo số lớp × head size.<br>*Dao động tùy kiến trúc* |
| **CUDA Runtime Context**<br>📌 *(tự động)*                                                         | `~0.1 – 0.5 GB`                        | CUDA cần VRAM cho kernel launch, memory pools...<br>*Thường nhỏ hơn 1 GB, dao động tùy driver và runtime.*                                                           |
| **Framework Buffers**<br>📌 `--enable-cuda-graphs`, tokenizer preload                              | `~0.3 – 1.0 GB`                        | **`--enable-cuda-graphs`**: tạo graph tăng tốc nhưng tăng usage.<br>**Tokenizer preload**: tốn RAM khi load tokenizer lên GPU.                                       |
| **Prefill & Padding Buffers**<br>📌 `--gpu-memory-utilization`, padding strategy, `PagedAttention` | `~0.2 – 0.8 GB`                        | **`--gpu-memory-utilization`**: giới hạn mức VRAM được dùng.<br>**Smart padding + PagedAttention**: giúp tối ưu prefill & tránh memory waste.                        |
| **Memory Fragmentation**<br>📌 *(runtime allocator)*                                               | `~5–10% tổng VRAM`                     | Gây lãng phí do phân bổ bộ nhớ không liên tục.<br>**PagedAttention**, **memory pool reuse** có thể giảm fragmentation.                                               |
| **Multi-Process Overhead**<br>📌 `nproc`, `multi-GPU`, `vLLM workers`                              | `~0.5 – 2.0 GB`                        | Chạy nhiều model/process trên cùng GPU gây overhead.<br>Mỗi worker/process có context riêng: model weights, cache, CUDA streams...                                   |

---

### 📌 **Bảng quy đổi nhanh: B → FP16 Model Size**

| Params | FP16 size | INT4 size (ước tính) |
| ------ | --------- | -------------------- |
| 1B     | \~2 GB    | \~0.5 GB             |
| 3B     | \~6 GB    | \~1.5 GB             |
| 7B     | \~13 GB   | \~3.3 GB             |
| 13B    | \~24 GB   | \~6.0 GB             |

---

### 🛠️ **Tối ưu hóa có thể bổ sung thêm nếu cần**:

| Tối ưu hóa              | Lợi ích chính                            |
| ----------------------- | ---------------------------------------- |
| **PagedAttention**      | Giảm KV cache fragmentation              |
| **Dynamic Memory Pool** | Tái sử dụng memory, giảm waste           |
| **Smart Batching**      | Tối ưu prefill & padding                 |
| **CUDA Graphs**         | Tăng tốc inference, giảm launch overhead |

---

