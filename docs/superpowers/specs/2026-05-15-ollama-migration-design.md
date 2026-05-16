# 将GLM模型替换为本地Ollama设计文档

**日期**: 2026-05-15
**状态**: 待实施

## 概述

将项目中使用的智谱AI GLM模型（glm-4-plus、glm-4）替换为本地Ollama服务提供的qwen3:14b模型，同时将embedding模型替换为nomic-embed-text。

## 目标

1. 将Java后端的LLM配置从GLM切换到本地Ollama
2. 将Python工具的LLM配置从GLM切换到本地Ollama
3. 将Python工具的Embedding配置从OpenAI切换到本地Ollama
4. 保持代码逻辑不变，仅修改配置和必要的接口调用

## 约束条件

- **不提交git**: 所有配置更改仅限本地使用
- **本地依赖**: 服务依赖Ollama在localhost:11434运行
- **模型要求**: qwen3:14b 和 nomic-embed-text 必须已安装

## 实施方案

### 第一部分：Java后端配置

**文件**: `genie-backend/src/main/resources/application.yml`

#### 1. LLM默认配置

修改 `llm.default` 部分：

| 配置项 | 原值 | 新值 |
|--------|------|------|
| `base_url` | `https://open.bigmodel.cn/api/coding/paas/v4` | `http://localhost:11434/v1` |
| `apikey` | `ee4e372fd87b463b8dab7b7850e71f30.ffewlhrfn53LUL4Q` | `ollama` |
| `model` | `glm-4-plus` | `qwen3:14b` |
| `interface_url` | `/chat/completions` | `/chat/completions` (保持不变) |

#### 2. LLM设置

修改 `llm.settings` JSON配置：

- 将 `glm-4-plus` 配置重命名为 `qwen3:14b`
- 将 `glm-4` 配置重命名为 `qwen3:14b`
- 更新 `baseUrl` 为 `http://localhost:11434/v1`
- 更新 `apiKey` 为 `ollama`

#### 3. 模型引用

修改所有 `model_name` 和 `default_model_name` 配置：

- `model_name: glm-4-plus` → `qwen3:14b`
- `default_model_name: glm-4-plus` → `qwen3:14b`

#### 4. Embedding配置

修改 `data-agent.qdrantConfig` 部分：

| 配置项 | 原值 | 新值 |
|--------|------|------|
| `embeddingUrl` | `http://xxxx.local` | `http://localhost:11434/api/embed` |

---

### 第二部分：Python工具配置

**文件**: `genie-tool/.env`

#### 1. OpenAI配置（用于litellm）

| 配置项 | 原值 | 新值 |
|--------|------|------|
| `OPENAI_API_KEY` | `ee4e372fd87b463b8dab7b7850e71f30.ffewlhrfn53LUL4Q` | `ollama` |
| `OPENAI_BASE_URL` | `https://open.bigmodel.cn/api/coding/paas/v4` | `http://localhost:11434/v1` |

#### 2. 默认模型

| 配置项 | 原值 | 新值 |
|--------|------|------|
| `DEFAULT_MODEL` | `openai/glm-4-plus` | `ollama/qwen3:14b` |

#### 3. 所有子模型配置

统一将以下配置从 `openai/glm-4-plus` 或 `gpt-4.*` 改为 `ollama/qwen3:14b`：

- `QUERY_DECOMPOSE_MODEL`
- `QUERY_DECOMPOSE_THINK_MODEL`
- `SEARCH_REASONING_MODEL`
- `SEARCH_ANSWER_MODEL`
- `REPORT_MODEL`
- `CODE_INTEPRETER_MODEL`
- `TR_EXTRACT_SYS_WSD_MODEL_NAME`
- `TR_TABLE_FILTER_MODEL_NAME`
- `TR_COLUMN_FILTER_MODEL_NAME`
- `CAL_ENGINE_MODEL`
- `ANALYSIS_MODEL`
- `NL2SQL_MODEL_NAME`
- `REWRITE_MODEL_NAME`
- `THINK_MODEL_NAME`

---

### 第三部分：Python Embedding配置

**文件**: `genie-tool/genie_tool/util/qdrant_utils.py`

#### 1. 修改 `get_embedding()` 函数

将使用OpenAI API改为使用Ollama本地API：

```python
def get_embedding(text):
    embedding_url = os.getenv("EMBEDDING_URL", "http://localhost:11434/api/embed")
    model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

    response = requests.post(
        embedding_url,
        json={"model": model, "input": text},
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()
    return response.json()['embeddings'][0]
```

#### 2. 新增环境变量

在 `.env` 文件中添加：

```bash
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_URL=http://localhost:11434/api/embed
```

---

### 第四部分：验证步骤

#### 1. 验证Ollama服务

```bash
# 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 验证模型已安装
ollama list
```

#### 2. 运行Python测试脚本

```bash
cd genie-tool
python test_ollama_integration.py
```

#### 3. 启动Java后端并测试

```bash
cd genie-backend
# 启动服务并测试
```

---

## 注意事项

1. **不提交git**: 所有配置更改仅限本地使用
2. **端口占用**: 确保11434端口没有被其他服务占用
3. **模型性能**: 本地模型性能取决于硬件配置（CPU/GPU）
4. **网络依赖**: 服务依赖Ollama本地运行
5. **API兼容性**: Ollama兼容OpenAI API格式，无需修改Java代码逻辑

## 需要修改的文件汇总

| 文件 | 修改类型 |
|------|---------|
| `genie-backend/src/main/resources/application.yml` | 配置替换 |
| `genie-tool/.env` | 配置替换 |
| `genie-tool/genie_tool/util/qdrant_utils.py` | 代码修改 |

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| Ollama服务未运行 | 服务不可用 | 启动前验证服务状态 |
| 模型未安装 | 调用失败 | 运行前验证模型列表 |
| 本地性能不足 | 响应慢 | 根据硬件调整期望 |
| API格式差异 | 调用失败 | Ollama兼容OpenAI格式，风险低 |
