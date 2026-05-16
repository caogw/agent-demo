#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ollama 集成测试脚本

用法:
    python test_ollama_integration.py

功能:
    - 测试 LLM 对话功能
    - 测试 Embedding 功能
    - 测试流式响应
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目路径到 sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

load_dotenv()


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_success(msg: str):
    """打印成功消息"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")


def print_error(msg: str):
    """打印错误消息"""
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def print_info(msg: str):
    """打印信息消息"""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")


def print_warning(msg: str):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")


def print_header(msg: str):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{msg.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


async def test_ollama_service():
    """测试 Ollama 服务是否可用"""
    print_header("测试 1: Ollama 服务连接")

    try:
        import requests

        ollama_url = os.getenv("OPENAI_BASE_URL", "http://localhost:11434")
        tags_url = f"{ollama_url.replace('/v1', '')}/api/tags"

        print_info(f"连接到: {tags_url}")

        response = requests.get(tags_url, timeout=5)

        if response.status_code == 200:
            models = response.json().get("models", [])
            print_success(f"Ollama 服务正常，已安装 {len(models)} 个模型")

            for model in models[:5]:  # 只显示前5个
                print(f"  - {model.get('name', 'unknown')}")

            if len(models) > 5:
                print(f"  ... 还有 {len(models) - 5} 个模型")

            return True
        else:
            print_error(f"Ollama 服务响应异常: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print_error("无法连接到 Ollama 服务")
        print_info("请确保 Ollama 正在运行: ollama serve")
        return False
    except Exception as e:
        print_error(f"连接失败: {str(e)}")
        return False


async def test_llm_completion():
    """测试 LLM 对话功能"""
    print_header("测试 2: LLM 对话功能")

    try:
        from genie_tool.util.llm_util import ask_llm

        model = os.getenv("DEFAULT_MODEL", "ollama/llama3.1:8b")
        messages = [{"role": "user", "content": "你好，请用一句话介绍你自己"}]

        print_info(f"使用模型: {model}")
        print_info("发送测试消息...")

        response_count = 0
        async for response in ask_llm(messages=messages, model=model, stream=False):
            if response_count == 0:
                print_success(f"LLM 响应: {response}")
                response_count += 1

        if response_count > 0:
            return True
        else:
            print_error("未收到响应")
            return False

    except ImportError as e:
        print_error(f"导入模块失败: {str(e)}")
        print_info("请确保已安装所有依赖: uv sync")
        return False
    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        return False


async def test_embedding():
    """测试 Embedding 功能"""
    print_header("测试 3: Embedding 功能")

    try:
        from genie_tool.util.qdrant_utils import get_embedding

        print_info("测试文本 embedding 生成...")

        text = "这是一段测试文本，用于验证 embedding 功能是否正常工作。"
        embedding = get_embedding(text)

        if embedding and len(embedding) > 0:
            print_success(f"Embedding 生成成功")
            print_info(f"向量维度: {len(embedding)}")
            print_info(f"向量预览 (前5个值): {embedding[:5]}")
            return True
        else:
            print_error("Embedding 生成失败")
            print_info("请确保 nomic-embed-text 模型已安装:")
            print_info("  ollama pull nomic-embed-text")
            return False

    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        return False


async def test_streaming():
    """测试流式响应"""
    print_header("测试 4: 流式响应")

    try:
        from genie_tool.util.llm_util import ask_llm

        model = os.getenv("DEFAULT_MODEL", "ollama/llama3.1:8b")
        messages = [{"role": "user", "content": "请从1数到5"}]

        print_info(f"使用模型: {model}")
        print_info("测试流式输出...\n")

        print("响应: ", end="", flush=True)
        chunk_count = 0
        full_response = ""

        async for chunk in ask_llm(messages=messages, model=model, stream=True, only_content=True):
            if chunk:
                print(chunk, end="", flush=True)
                full_response += chunk
                chunk_count += 1

        print()  # 换行

        if chunk_count > 0 and len(full_response) > 0:
            print_success(f"流式响应成功 (收到 {chunk_count} 个 chunk)")
            return True
        else:
            print_error("未收到流式响应")
            return False

    except Exception as e:
        print_error(f"测试失败: {str(e)}")
        return False


async def test_environment_config():
    """测试环境配置"""
    print_header("测试 0: 环境配置检查")

    required_vars = {
        "OPENAI_API_KEY": "ollama",
        "OPENAI_BASE_URL": "http://localhost:11434/v1",
        "DEFAULT_MODEL": None,  # 只检查存在，不检查值
    }

    all_ok = True

    for var_name, expected_value in required_vars.items():
        value = os.getenv(var_name)

        if value is None:
            print_error(f"环境变量 {var_name} 未设置")
            all_ok = False
        elif expected_value and value != expected_value:
            print_warning(f"{var_name} = {value} (预期: {expected_value})")
        else:
            print_success(f"{var_name} = {value}")

    # 检查 embedding 配置
    embedding_model = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    print_info(f"Embedding 模型: {embedding_model}")

    return all_ok


async def run_all_tests():
    """运行所有测试"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║        Ollama 集成测试                                    ║")
    print("║        Ollama Integration Test Suite                     ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")

    tests = [
        ("环境配置检查", test_environment_config),
        ("Ollama 服务连接", test_ollama_service),
        ("LLM 对话功能", test_llm_completion),
        ("Embedding 功能", test_embedding),
        ("流式响应", test_streaming),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"{test_name} 抛出异常: {str(e)}")
            results.append((test_name, False))

    # 打印测试结果汇总
    print_header("测试结果汇总")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = f"{Colors.GREEN}通过{Colors.END}" if result else f"{Colors.RED}失败{Colors.END}"
        print(f"  {test_name}: {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 所有测试通过！Ollama 集成成功！{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}⚠️  部分测试失败，请检查配置和服务状态{Colors.END}\n")
        return 1


def main():
    """主函数"""
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_warning("\n测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print_error(f"测试程序异常: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
