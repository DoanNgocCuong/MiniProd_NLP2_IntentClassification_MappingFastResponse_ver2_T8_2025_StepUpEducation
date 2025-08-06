Read file: tuning/Dockerfile

Hai file này có vai trò khác nhau trong quy trình Docker:

## `build_env.sh` - **XÂY DỰNG** Docker Image
```bash
docker build -t llm-unsloth:latest .
```
**Mục đích:** 
- Tạo ra Docker image từ `Dockerfile`
- Cài đặt môi trường với PyTorch + Unsloth library
- **Chỉ chạy 1 lần** khi setup lần đầu (hoặc khi cần update)

## `run_env.sh` - **KHỞI ĐỘNG** Container
```bash
docker run --gpus all -it --rm --name llm-unsloth -v $(pwd):/workspace -w /workspace llm-unsloth:latest
```

```bash
 3d [ubuntu@mgc-dev2-3090:~/hoailb/ … /MiniProd_NLP2_IntentClassification_MappingFastResponse_ver2_T8_2025_StepUpEducation/tuning]└4 <base> main* ± docker run --gpus all -it --rm --name llm-unsloth -v $(pwd):/workspace -w /workspace llm-unsloth:latest

=============
== PyTorch ==
=============

NVIDIA Release 23.09 (build 69180607)
PyTorch Version 2.1.0a0+32f93b1

Container image Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

Copyright (c) 2014-2023 Facebook Inc.
Copyright (c) 2011-2014 Idiap Research Institute (Ronan Collobert)
Copyright (c) 2012-2014 Deepmind Technologies    (Koray Kavukcuoglu)
Copyright (c) 2011-2012 NEC Laboratories America (Koray Kavukcuoglu)
Copyright (c) 2011-2013 NYU                      (Clement Farabet)
Copyright (c) 2006-2010 NEC Laboratories America (Ronan Collobert, Leon Bottou, Iain Melvin, Jason Weston)
Copyright (c) 2006      Idiap Research Institute (Samy Bengio)
Copyright (c) 2001-2004 Idiap Research Institute (Ronan Collobert, Samy Bengio, Johnny Mariethoz)
Copyright (c) 2015      Google Inc.
Copyright (c) 2015      Yangqing Jia
Copyright (c) 2013-2016 The Caffe contributors
All rights reserved.

Various files include modifications (c) NVIDIA CORPORATION & AFFILIATES.  All rights reserved.

This container image and its contents are governed by the NVIDIA Deep Learning Container License.
By pulling and using the container, you accept the terms and conditions of this license:
https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license

WARNING: CUDA Minor Version Compatibility mode ENABLED.
  Using driver version 530.41.03 which has support for CUDA 12.1.  This container
  was built with CUDA 12.2 and will be run in Minor Version Compatibility mode.
  CUDA Forward Compatibility is preferred over Minor Version Compatibility for use
  with this container but was unavailable:
  [[System has unsupported display driver / cuda driver combination (CUDA_ERROR_SYSTEM_DRIVER_MISMATCH) cuInit()=803]]
  See https://docs.nvidia.com/deploy/cuda-compatibility/ for details.

NOTE: The SHMEM allocation limit is set to the default of 64MB.  This may be
   insufficient for PyTorch.  NVIDIA recommends the use of the following flags:
   docker run --gpus all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 ...

root@3a9cfc16c74c:/workspace# 
```

**Mục đích:**
- Khởi động container từ image đã build
- Kết nối GPU, thư mục làm việc
- **Chạy mỗi khi** muốn bắt đầu làm việc

## Quy trình sử dụng:
1. **Lần đầu:** `bash build_env.sh` (build image)
2. **Mỗi lần dùng:** `bash run_env.sh` (start container)

**Ví dụ tương tự:**
- `build_env.sh` = xây nhà (1 lần)
- `run_env.sh` = mở cửa vào nhà (mỗi khi cần)

**💡 Lưu ý:** Nếu image `llm-unsloth:latest` chưa tồn tại, bạn phải chạy `build_env.sh` trước!

**Đúng rồi!** 🎉 

Mọi thứ đã hoạt động thành công:

✅ **Build image:** Thành công (dòng 182)
✅ **Start container:** Thành công  
✅ **Vào container:** Thành công - bạn đang ở trong container (prompt `root@...:/workspace#`)

**⚠️ Warnings nhỏ (không ảnh hưởng):**
- **CUDA compatibility:** Driver cũ hơn CUDA trong container một chút, nhưng vẫn work
- **SHMEM limit:** Có thể cần tăng nếu training model lớn

**🚀 Bây giờ bạn có thể:**
```bash
# Kiểm tra files
ls -la

# Chạy fine-tune 
python finetune_unsloth_chatml.py

# Hoặc test GPU
nvidia-smi
```

**Môi trường đã sẵn sàng để fine-tune model!** Container đang chạy PyTorch 2.1.0 với Unsloth library đã được cài đặt.


----
