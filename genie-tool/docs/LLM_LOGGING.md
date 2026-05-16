# LLM 调用日志说明

## 概述

为 `genie-tool` 项目添加了大模型请求和响应的详细日志功能，方便观察和调试模型调用情况。

## 功能特性

### 1. 请求日志
记录每次LLM调用的详细信息：
- 时间戳
- 模型名称
- 温度、top_p等参数
- 消息数量和内容长度预览
- 额外参数

### 2. 响应日志
记录LLM响应的详细信息：
- 时间戳
- 响应模型
- Token使用情况（prompt_tokens, completion_tokens, total_tokens）
- 内容预览（前200个字符）

### 3. 流式输出日志
针对流式调用：
- 流式开始标记
- 流式结束统计（总内容长度、chunk数量）

### 4. 错误日志
记录调用过程中的异常：
- 错误时间戳
- 模型名称
- 错误类型和消息

## 使用方法

### 基本使用

```python
from genie_tool.util.llm_util import ask_llm

# 你的现有代码无需修改，日志会自动记录
async for response in ask_llm(
    messages="你好",
    model="ollama/qwen2.5",
    temperature=0.7,
    only_content=True
):
    print(response)
```

### 自定义日志配置

```python
from genie_tool.util.llm_logging_config import setup_llm_logging

# 配置日志系统
setup_llm_logging(
    log_to_console=True,      # 输出到控制台
    log_to_file=True,         # 输出到文件
    log_file_path="logs/llm_{time:YYYY-MM-DD}.log",  # 文件路径模板
    log_level="INFO",         # 日志级别
    include_request_content=False,  # 是否记录完整请求内容
    include_response_content=False, # 是否记录完整响应内容
    max_content_length=200    # 内容预览长度
)
```

### 测试日志功能

运行测试脚本查看日志效果：

```bash
cd genie-tool
python test_llm_logging.py
```

## 日志示例

### 请求日志
```json
{
  "timestamp": "2025-01-16T10:30:45.123456",
  "request_type": "llm_call",
  "model": "ollama/qwen2.5",
  "temperature": 0.7,
  "top_p": null,
  "stream": false,
  "messages_count": 1,
  "messages_preview": [
    {"role": "user", "content_length": 50}
  ],
  "extra_params": {}
}
```

### 响应日志
```json
{
  "timestamp": "2025-01-16T10:30:47.789012",
  "response_type": "llm_response",
  "model": "ollama/qwen2.5",
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 150,
    "total_tokens": 175
  },
  "only_content": true
}
```

## 日志文件位置

- **默认路径**: `genie-tool/logs/llm_YYYY-MM-DD.log`
- **轮转策略**: 每天午夜创建新文件
- **保留时间**: 7天
- **压缩**: 旧日志文件自动压缩为zip格式

## 配置选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `log_to_console` | 是否输出到控制台 | `true` |
| `log_to_file` | 是否输出到文件 | `true` |
| `log_level` | 日志级别 | `"INFO"` |
| `include_request_content` | 记录完整请求内容 | `false` |
| `include_response_content` | 记录完整响应内容 | `false` |
| `max_content_length` | 内容预览长度 | `200` |

## 性能影响

- 日志记录对性能影响很小（<1ms）
- 建议生产环境保持默认配置（不记录完整内容）
- 调试时可临时启用完整内容记录

## 故障排查

### 日志未输出
1. 检查日志级别设置
2. 确认日志目录有写权限
3. 查看是否有错误日志输出

### 日志文件过大
1. 调整 `retention` 参数
2. 设置 `include_request_content=False`
3. 设置 `include_response_content=False`

## 相关文件

- `genie_tool/util/llm_util.py` - 主要LLM调用函数
- `genie_tool/util/llm_logging_config.py` - 日志配置
- `test_llm_logging.py` - 测试脚本
- `genie_tool/util/litellm_ollama_patch.py` - litellm补丁
