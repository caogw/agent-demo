# M4 Pro GPU 加速配置完成

## ✅ 配置结果

### 性能对比
- **CPU 版本 (qwen3:14b)**: ~54 秒
- **GPU 版本 (qwen3:14b-m4gpu)**: ~12 秒
- **性能提升**: 约 4.5 倍 ⚡

### 资源使用优化
- CPU 使用率: 从 29% 降至更低
- 内存占用: 保持 9.3GB
- GPU 利用率: Metal (MPS) 已启用

## 📋 配置详情

### 模型配置文件
位置: `genie-tool/models/Modelfile.qwen3-14b-gpu`

关键参数:
```bash
PARAMETER num_gpu 99          # 使用 99% GPU 层
PARAMETER num_thread 10       # CPU 线程数 (M4 Pro 20 核优化)
PARAMETER num_ctx 4096        # 上下文长度
PARAMETER num_batch 512       # 批处理大小
```

### 环境变量已更新
所有模型配置已切换到 GPU 版本:
- `DEFAULT_MODEL=ollama/qwen3:14b-m4gpu`
- `QUERY_DECOMPOSE_MODEL=ollama/qwen3:14b-m4gpu`
- `SEARCH_REASONING_MODEL=ollama/qwen3:14b-m4gpu`
- `CODE_INTEPRETER_MODEL=ollama/qwen3:14b-m4gpu`
- `NL2SQL_MODEL_NAME=ollama/qwen3:14b-m4gpu`
- 等等...

## 🔧 验证 GPU 加速

### 方法 1: 性能测试
```bash
# CPU 版本
time ollama run qwen3:14b "你好"

# GPU 版本
time ollama run qwen3:14b-m4gpu "你好"

# GPU 版本应该快 3-5 倍
```

### 方法 2: 监控 GPU 使用
```bash
# 安装 asitop
pip install asitop

# 运行监控
asitop

# 查找 GPU 频率
ioreg -l | grep -i "performance-state"
```

### 方法 3: 检查 Ollama 进程
```bash
ps aux | grep ollama
# 查看 CPU % 是否降低
```

## 🚀 进一步优化

### 1. 调整 GPU 层数
如果 GPU 内存不足，可以减少 `num_gpu`:
```bash
PARAMETER num_gpu 50  # 使用 50% GPU 层
```

### 2. 调整线程数
根据系统负载调整:
```bash
PARAMETER num_thread 8   # 更少线程，更省电
PARAMETER num_thread 12  # 更多线程，更快速度
```

### 3. 使用更小的模型
对于日常开发，可以考虑 7B 模型:
```bash
ollama pull qwen2.5:7b
# 创建 GPU 版本...
# 更新 DEFAULT_MODEL=ollama/qwen2.5:7b
```

## ⚠️ 注意事项

1. **首次运行**: 第一次使用 GPU 版本时会较慢（加载模型到 GPU）
2. **热量产生**: GPU 加速仍会产生热量，但比纯 CPU 运行少
3. **内存占用**: 14B 模型需要约 9-10GB 内存
4. **电池续航**: 使用 GPU 会影响笔记本电脑的电池续航

## 📊 监控脚本

运行 GPU 使用检查:
```bash
bash /Users/caogw/cgw-dev/gitrepo/agent-demo/genie-tool/scripts/check_gpu_usage.sh
```

## 🎯 下一步建议

1. **测试应用**: 使用新配置运行你的应用，验证性能
2. **监控温度**: 运行 asitop 查看 GPU 使用率和温度
3. **调整参数**: 根据实际使用情况调整 num_thread 和 num_gpu

## 📝 故障排除

### 如果 GPU 没有启用:
1. 检查 Ollama 版本: `ollama --version` (需要 >= 0.1.20)
2. 重新创建模型: `ollama create qwen3:14b-m4gpu -f models/Modelfile.qwen3-14b-gpu`
3. 检查 Metal 支持: `system_profiler SPDisplaysDataType`

### 如果仍然发烫:
1. 减少线程数: `PARAMETER num_thread 6`
2. 使用更小的模型: qwen2.5:7b
3. 关闭其他应用释放内存

---
创建时间: 2026-05-16
配置设备: Apple M4 Pro (20 核)
