#!/bin/bash
# Ollama GPU 加速配置脚本
# 适用于 Apple Silicon (M1/M2/M3/M4)

echo "=== Ollama GPU 优化配置 ==="
echo ""

# 1. 停止所有运行的模型
echo "1. 停止所有运行的模型..."
pkill -f "ollama runner" 2>/dev/null || true
sleep 2

# 2. 检查系统 GPU 核心数
if command -v sysctl &> /dev/null; then
    GPU_CORES=$(sysctl -n hw.perflevel0.physicalcpu 2>/dev/null || echo "4")
    echo "2. 检测到 $GPU_CORES 个性能核心"
fi

# 3. 为 qwen3:14b 创建优化的 Modelfile
echo "3. 创建优化的模型配置..."
cat > /tmp/qwen3_gpu_modelfile << 'EOF'
FROM qwen3:14b

# 参数配置
PARAMETER num_gpu 99  # 使用 99% 的 GPU 层
PARAMETER num_thread 8  # 限制 CPU 线程数
PARAMETER num_ctx 4096  # 上下文长度

# 性能优化
PARAMETER repeat_last_n 64
PARAMETER repeat_penalty 1.1
PARAMETER temperature 0.8
PARAMETER top_p 0.9
PARAMETER top_k 40
EOF

# 4. 创建 GPU 优化版本的模型
echo "4. 创建 GPU 优化版本..."
ollama create qwen3:14b-gpu -f /tmp/qwen3_gpu_modelfile

echo ""
echo "=== 配置完成 ==="
echo "使用方法："
echo "  测试 GPU 版本: ollama run qwen3:14b-gpu"
echo "  更新环境变量: export DEFAULT_MODEL=ollama/qwen3:14b-gpu"
echo ""
echo "检查 GPU 使用情况："
echo "  sudo powermetrics --samplers gpu_power -i 1000"
echo ""
