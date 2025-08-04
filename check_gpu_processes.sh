#!/bin/bash

# =============================================================================  
# 🔍 SCRIPT XÁC ĐỊNH THỨ MỤC CỦA CÁC GPU PROCESSES
# =============================================================================

echo "🔍 Checking GPU processes directories..."
echo "======================================"

# Lấy danh sách PID từ nvidia-smi
nvidia_pids=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits)

if [ -z "$nvidia_pids" ]; then
    echo "❌ No GPU processes found!"
    exit 1
fi

echo "📊 Found GPU processes:"
echo

for pid in $nvidia_pids; do
    echo "🔹 PID: $pid"
    
    # Kiểm tra process có tồn tại không
    if [ ! -d "/proc/$pid" ]; then
        echo "   ❌ Process not found (may have ended)"
        echo
        continue
    fi
    
    # Lấy thông tin process
    process_name=$(ps -p $pid -o comm= 2>/dev/null || echo "Unknown")
    working_dir=$(pwdx $pid 2>/dev/null | cut -d' ' -f2-)
    
    # Lấy command line
    cmdline=$(cat /proc/$pid/cmdline 2>/dev/null | tr '\0' ' ' | cut -c1-100)
    
    # Lấy GPU memory usage
    gpu_memory=$(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader,nounits | grep "^$pid" | cut -d',' -f2)
    
    echo "   📁 Process: $process_name"
    echo "   📂 Directory: $working_dir"
    echo "   💾 GPU Memory: ${gpu_memory}MiB"
    echo "   💻 Command: $cmdline"
    echo
done

echo "======================================"
echo "🎯 Tip: Dùng 'cd' đến thư mục để kiểm tra project!"