#!/bin/bash
# GPU 使用检查脚本 - 适用于 Apple Silicon

echo "=== Ollama GPU 使用检查 ==="
echo ""

# 方法 1: 使用 powermetrics（需要 sudo）
echo "方法 1: 使用 powermetrics 检查 GPU 功率"
echo "运行: sudo powermetrics --samplers gpu_power -i 1000 -n 5"
echo ""

# 方法 2: 使用 asitop（如果安装）
if command -v asitop &> /dev/null; then
    echo "方法 2: 使用 asitop"
    echo "运行: asitop"
else
    echo "方法 2: 安装 asitop（推荐）"
    echo "pip install asitop"
    echo "然后运行: asitop"
fi

echo ""

# 方法 3: 检查进程状态
echo "方法 3: 检查 Ollama 进程"
ps aux | grep -E "ollama|qwen" | grep -v grep | awk '{printf "CPU: %s%%, MEM: %s%%, CMD: %s\n", $3, $4, $11}' | head -5

echo ""

# 方法 4: 使用 ioreg 检查 GPU 状态
echo "方法 4: 检查 GPU 频率"
ioreg -l | grep -i "performance-state" | head -3

echo ""
echo "=== 快速测试命令 ==="
echo ""
echo "测试 CPU 版本："
echo "  time ollama run qwen3:14b '你好'"
echo ""
echo "测试 GPU 版本："
echo "  time ollama run qwen3:14b-m4gpu '你好'"
echo ""
echo "比较两次测试的时间，GPU 版本应该更快。"
