#!/bin/bash
# CPU 使用检查和优化脚本

echo "=== 系统资源使用情况 ==="
echo ""

echo "1. 总体 CPU 使用情况:"
top -l 1 | head -12 | tail -6
echo ""

echo "2. Python 进程 CPU 使用:"
ps aux | grep -E "python|uvicorn" | grep -v grep | awk '{printf "PID: %s, CPU: %s%%, MEM: %s%%, CMD: %s\n", $2, $3, $4, $11}' | head -10
echo ""

echo "3. Ollama 进程:"
ps aux | grep ollama | grep -v grep | awk '{printf "PID: %s, CPU: %s%%, MEM: %s%%\n", $2, $3, $4}' | head -5
echo ""

echo "4. 高 CPU 进程 (>5%):"
ps aux | awk '$3 > 5.0 {printf "PID: %s, CPU: %s%%, MEM: %s%%, CMD: %s\n", $2, $3, $4, $11}' | head -10
echo ""

echo "5. 内存使用:"
vm_stat | head -10
echo ""

echo "=== 优化建议 ==="
echo ""
echo "如果 CPU 使用率过高："
echo "1. 重启 server.py（已关闭 reload）"
echo "   pkill -f 'server.py' && uv run python server.py &"
echo ""
echo "2. 减少并发 workers"
echo "   uv run python server.py --workers 1"
echo ""
echo "3. 检查是否有无限循环的后台任务"
echo "   ps aux | grep python"
echo ""
echo "4. 监控实时 CPU 使用"
echo "   top -o cpu -n 10"
echo ""
