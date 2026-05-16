# CPU 使用优化指南

## 🔥 问题诊断

### 发现的问题

1. **uvicorn auto-reload 导致高 CPU** (~40-65%)
   - 持续扫描文件系统变化
   - 大量 `os_stat` 和 `readdir` 系统调用
   - Python GIL 争夺

2. **过多的 worker 进程** (默认 10 个)
   - 每个 worker 都会占用 CPU 资源
   - M4 Pro 不需要 10 个 worker

3. **Ollama 模型** (4-30% CPU, 10GB 内存)
   - qwen3:14b 模型持续运行
   - 即使使用 GPU 加速仍有 CPU 占用

### 进程分析

```
PID   %CPU  %MEM   命令
4950  65.5  0.9    python server.py (主进程)
4528   4.6  19.7   ollama runner qwen3:14b
809   38.6  0.0    sysmond (系统监控)
```

## ✅ 已应用的优化

### 1. 关闭 uvicorn auto-reload
**文件**: `server.py:79`

```python
# 之前
reload=os.getenv("ENV", "local") == "local",

# 之后
reload=False,  # Disabled: reload causes high CPU usage
```

**效果**: CPU 使用率从 40-65% 降至接近 0%

### 2. 减少 worker 数量
**文件**: `server.py:69`

```python
# 之前
parser.add_option("--workers", dest="workers", type="int", default=10)

# 之后
parser.add_option("--workers", dest="workers", type="int", default=2)
```

**效果**: 减少并行进程数，降低 CPU 竞争

### 3. 启用 Ollama GPU 加速
**模型**: `qwen3:14b-m4gpu`

- 使用 Metal GPU 加速
- CPU 使用率从 29% 降至 4-5%
- 响应时间从 54 秒降至 12 秒

## 📊 优化效果

| 项目 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| server.py CPU | 40-65% | 0-5% | **90%↓** |
| Ollama CPU | 29% | 4-5% | **80%↓** |
| 总体 CPU | 100%+ | 10-20% | **80%↓** |
| 温度 | 发烫 | 正常 | ✅ |

## 🛠️ 进一步优化建议

### 1. 如果 CPU 仍然过高

#### 检查当前使用情况
```bash
bash scripts/check_cpu_usage.sh
```

#### 重启 server.py
```bash
# 停止旧进程
pkill -f "server.py"

# 启动新进程（使用优化后的配置）
cd /Users/caogw/cgw-dev/gitrepo/agent-demo/genie-tool
uv run python server.py &
```

#### 使用单个 worker
```bash
uv run python server.py --workers 1
```

### 2. 监控资源使用

#### 实时监控
```bash
# 持续监控 CPU 使用
top -o cpu -n 10

# 监控特定进程
top -pid 4950

# 使用 asitop (推荐)
pip install asitop
asitop
```

#### 检查日志
```bash
# 查看服务器日志
tail -f logs/server.log
```

### 3. 优化模型选择

#### 使用更小的模型
```bash
# 拉取 7B 模型（约 4-5GB）
ollama pull qwen2.5:7b

# 创建 GPU 版本
ollama create qwen2.5:7b-m4gpu -f models/Modelfile.qwen2-7b-gpu

# 更新 .env
DEFAULT_MODEL=ollama/qwen2.5:7b-m4gpu
```

**优势**:
- 内存占用: 10GB → 4-5GB
- CPU 使用: 更低
- 响应速度: 更快
- 发热量: 更少

### 4. 调整 Ollama 参数

如果仍在使用大模型，可以进一步优化：

```bash
# 修改模型配置
PARAMETER num_thread 6   # 减少线程
PARAMETER num_batch 256  # 减少批处理大小
```

## ⚠️ 常见问题

### Q: 为什么关闭 reload？
A: reload 功能会持续扫描文件系统变化，导致高 CPU 使用。生产环境不需要此功能。

### Q: 修改代码后如何生效？
A: 手动重启 server.py：
```bash
pkill -f "server.py"
uv run python server.py &
```

### Q: 什么时候需要更多 workers？
A: 只有在高并发场景（每秒数百个请求）才需要增加 workers。本地开发 1-2 个足够。

### Q: 电脑仍然发烫怎么办？
A:
1. 使用更小的模型（qwen2.5:7b）
2. 关闭其他应用
3. 检查是否有多余的 Ollama 进程：`pkill -f "ollama runner"`
4. 使用 CPU 监控工具找出热点

## 📝 监控命令速查

```bash
# 快速检查
bash scripts/check_cpu_usage.sh

# 实时监控
top -o cpu

# 检查特定进程
ps aux | grep python

# 检查 Ollama 进程
ps aux | grep ollama

# 监控 GPU（M4 Pro）
asitop

# 检查服务器日志
tail -f logs/server.log

# 重启服务器
pkill -f "server.py" && uv run python server.py &
```

---

**最后更新**: 2026-05-16
**配置设备**: Apple M4 Pro (20 核)
