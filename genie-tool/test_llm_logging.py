# -*- coding: utf-8 -*-
"""
LLM日志测试脚本
用于测试和演示ask_llm函数的日志功能
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from genie_tool.util.llm_util import ask_llm
from loguru import logger


async def test_basic_llm_call():
    """测试基本的LLM调用（非流式）"""
    logger.info("=== 测试1: 基本LLM调用 ===")

    try:
        async for response in ask_llm(
            messages="你好，请简单介绍一下你自己",
            model="ollama/qwen2.5",  # 根据你的配置修改模型
            temperature=0.7,
            only_content=True
        ):
            logger.info(f"收到响应: {response[:100]}...")

    except Exception as e:
        logger.error(f"测试失败: {e}")


async def test_streaming_llm_call():
    """测试流式LLM调用"""
    logger.info("=== 测试2: 流式LLM调用 ===")

    try:
        async for chunk in ask_llm(
            messages="请写一首简短的诗",
            model="ollama/qwen2.5",
            temperature=0.8,
            stream=True,
            only_content=True
        ):
            print(chunk, end='', flush=True)

        print()  # 换行

    except Exception as e:
        logger.error(f"测试失败: {e}")


async def test_conversation_llm_call():
    """测试对话形式的LLM调用"""
    logger.info("=== 测试3: 对话形式LLM调用 ===")

    messages = [
        {"role": "system", "content": "你是一个有帮助的助手"},
        {"role": "user", "content": "什么是人工智能？"}
    ]

    try:
        async for response in ask_llm(
            messages=messages,
            model="ollama/qwen2.5",
            temperature=0.5,
            only_content=False
        ):
            if hasattr(response, 'usage'):
                logger.info(f"Token使用情况: {response.usage}")

    except Exception as e:
        logger.error(f"测试失败: {e}")


async def main():
    """主测试函数"""
    # 配置日志输出到文件和控制台
    logger.remove()  # 移除默认处理器

    # 控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )

    # 文件输出（按日期和大小轮转）
    logger.add(
        "logs/llm_{time:YYYY-MM-DD}.log",
        rotation="00:00",  # 每天午夜轮转
        retention="7 days",  # 保留7天
        compression="zip",  # 压缩旧日志
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )

    # 运行测试
    await test_basic_llm_call()
    await test_streaming_llm_call()
    await test_conversation_llm_call()


if __name__ == "__main__":
    asyncio.run(main())
