```bash
buntu@mgc-dev2-3090:~/hoailb/ … /MiniProd_NLP2_IntentClassification_MappingFastResponse_ver2_T8_2025_StepUpEducation]└4 <base> main(+10/-13)* ± nvidia-smi
Mon Aug  4 14:54:21 2025       
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 530.41.03              Driver Version: 530.41.03    CUDA Version: 12.1     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                  Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf            Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA GeForce RTX 3090         Off| 00000000:3B:00.0 Off |                  N/A |
| 36%   29C    P8                9W / 350W|  24238MiB / 24576MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
|   1  NVIDIA GeForce RTX 3090         Off| 00000000:AF:00.0 Off |                  N/A |
| 30%   27C    P8                8W / 350W|  16190MiB / 24576MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
|   2  NVIDIA GeForce RTX 3090         Off| 00000000:D8:00.0 Off |                  N/A |
| 76%   73C    P2              345W / 350W|  13152MiB / 24576MiB |    100%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
                                                                                         
+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
|    0   N/A  N/A     17500      C   tritonserver                               4162MiB |
|    0   N/A  N/A     23160      C   ...s/python/triton_python_backend_stub     9304MiB |
|    0   N/A  N/A     95412      C   python                                    10764MiB |
|    1   N/A  N/A     55743      C   python                                      524MiB |
|    1   N/A  N/A     55886      C   python                                      524MiB |
|    1   N/A  N/A     56119      C   python                                      524MiB |
|    1   N/A  N/A     56206      C   python                                      524MiB |
|    1   N/A  N/A     68435      C   gunicorn: worker [intent_api:app]          2928MiB |
|    1   N/A  N/A     84388      C   python                                     1430MiB |
|    1   N/A  N/A     95412      C   python                                     9734MiB |
|    2   N/A  N/A     34601      C   python                                    12526MiB |
|    2   N/A  N/A     95412      C   python                                      624MiB |
+---------------------------------------------------------------------------------------+
θ63° 3d [ubuntu@mgc-dev2-3090:~/hoailb/ … /MiniProd_NLP2_IntentClassification_MappingFastResponse_ver2_T8_2025_StepUpEducation]└4 <base> main(+10/-13)* ± 
```


## Nhận xét về các thông số GPU lúc này. 

## Nhận xét tình trạng GPU hiện tại:

**🔴 GPU 0**: **Overloaded** - 98.6% memory (24.2GB/24.6GB), gần như đầy, không thể chạy thêm gì.

**🟡 GPU 1**: **Busy** - 65.9% memory (16.2GB/24.6GB), đang chạy nhiều processes nhưng còn ~8GB trống.

**🟡 GPU 2**: **Heavy Load** - 53.5% memory (13.1GB/24.6GB) nhưng **100% utilization**, đang chạy intensive task (PID 34601 dùng 12.5GB).

### Tóm tắt:
- **Total memory used**: ~53.5GB/73.7GB (72.6%)
- **Available**: ~20GB spread across GPUs
- **Best option for vLLM**: **GPU 1** - có 8GB trống và ổn định nhất
- **Avoid**: GPU 0 (quá đầy), GPU 2 (đang 100% util)

**Recommendation**: Stick với GPU 1 trong script hiện tại, đã set `--gpu-memory-utilization 0.6` để an toàn.


---

# Các thông số có thể quan sát được từ nvidia-smi

## Các chỉ số quan sát được từ `nvidia-smi`:

### 🔧 **Header Information:**
- **Driver Version**: Phiên bản NVIDIA driver (530.41.03)
- **CUDA Version**: Phiên bản CUDA hỗ trợ (12.1)

### 🎯 **Per-GPU Metrics:**

#### **1. Basic Info:**
- **GPU ID**: Số thứ tự GPU (0, 1, 2...)
- **Name**: Tên card đồ họa (NVIDIA GeForce RTX 3090)
- **Bus-Id**: PCI bus address (00000000:3B:00.0)

#### **2. Power & Thermal:**
- **Fan**: Tốc độ quạt % (36%, 30%, 76%)
- **Temp**: Nhiệt độ °C (29C, 27C, 73C)
- **Pwr:Usage/Cap**: Công suất hiện tại/tối đa (9W/350W, 345W/350W)

#### **3. Performance:**
- **Perf**: Performance state (P0=max, P8=idle, P2=high performance)
- **GPU-Util**: % GPU đang sử dụng (0%, 42%, 100%)

#### **4. Memory:**
- **Memory-Usage**: RAM đã dùng/tổng (24238MiB/24576MiB)
- **Volatile Uncorr. ECC**: Lỗi memory (thường N/A cho consumer GPU)

#### **5. Status Flags:**
- **Persistence-M**: Persistence mode (On/Off)
- **Disp.A**: Display attached (On/Off)
- **Compute M.**: Compute mode (Default, Exclusive, Prohibited)
- **MIG M.**: Multi-Instance GPU mode (Enabled/Disabled)

### 📋 **Process Information:**
- **GPU**: GPU nào đang chạy process
- **PID**: Process ID
- **Type**: Loại process (C=Compute, G=Graphics, C+G=Both)
- **Process name**: Tên chương trình
- **GPU Memory Usage**: Memory process đó đang dùng

### 🚨 **Chỉ số cần chú ý:**

**🔥 High Load Indicators:**
- Power > 200W (GPU đang work hard)
- Temp > 70°C (nóng)
- GPU-Util > 80% (busy)
- Fan > 70% (cooling hard)

**✅ Idle Indicators:**
- Power < 50W
- Temp < 40°C
- GPU-Util = 0%
- Performance state P8

**⚠️ Warning Signs:**
- Temp > 85°C (quá nóng)
- Memory gần 100% (risk OOM)
- Power = Max (thermal throttling risk)