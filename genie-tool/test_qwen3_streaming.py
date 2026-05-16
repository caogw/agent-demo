#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 qwen3:14b 流式响应的不同参数配置
"""
import asyncio
import os
from dotenv import load_dotenv
from litellm import acompletion

load_dotenv()

async def test_streaming_with_options():
    """测试不同的参数配置"""
    model = "ollama/qwen3:14b"
    messages = [{"role": "user", "content": "请从1数到5"}]

    print("测试1: 默认配置")
    print("=" * 50)
    try:
        response = await acompletion(
            model=model,
            messages=messages,
            stream=True,
        )
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"错误: {e}\n")

    print("测试2: 使用 extra_body 禁用 thinking")
    print("=" * 50)
    try:
        response = await acompletion(
            model=model,
            messages=messages,
            stream=True,
            extra_body={
                "options": {
                    "num_ctx": 2048,
                    "temperature": 0.7
                }
            }
        )
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"错误: {e}\n")

    print("测试3: 非流式响应")
    print("=" * 50)
    try:
        response = await acompletion(
            model=model,
            messages=messages,
            stream=False,
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"错误: {e}\n")

if __name__ == "__main__":
    asyncio.run(test_streaming_with_options())
