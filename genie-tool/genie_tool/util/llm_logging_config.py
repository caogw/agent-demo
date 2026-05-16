# -*- coding: utf-8 -*-
"""
LLM日志配置
用于配置LLM调用的日志行为
"""
from loguru import logger
import sys
import os


def setup_llm_logging(
    log_to_console: bool = True,
    log_to_file: bool = True,
    log_file_path: str = "logs/llm_{time:YYYY-MM-DD}.log",
    log_level: str = "INFO",
    include_request_content: bool = False,
    include_response_content: bool = False,
    max_content_length: int = 200
):
    """
    配置LLM日志系统

    Args:
        log_to_console: 是否输出到控制台
        log_to_file: 是否输出到文件
        log_file_path: 日志文件路径模板
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        include_request_content: 是否在日志中包含完整的请求内容
        include_response_content: 是否在日志中包含完整的响应内容
        max_content_length: 内容预览的最大长度
    """
    # 移除默认处理器
    logger.remove()

    # 定义日志格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} - "
        "{message}"
    )

    # 控制台日志
    if log_to_console:
        logger.add(
            sys.stderr,
            format=console_format,
            level=log_level,
            colorize=True
        )

    # 文件日志
    if log_to_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file_path.replace("{time:YYYY-MM-DD}", "2024-01-01"))
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        logger.add(
            log_file_path,
            rotation="00:00",  # 每天午夜轮转
            retention="7 days",  # 保留7天
            compression="zip",  # 压缩旧日志
            format=file_format,
            level=log_level,
            encoding="utf-8"
        )

    # 将配置保存到环境变量，供llm_util使用
    os.environ["LLM_LOG_INCLUDE_REQUEST"] = str(include_request_content)
    os.environ["LLM_LOG_INCLUDE_RESPONSE"] = str(include_response_content)
    os.environ["LLM_LOG_MAX_CONTENT_LENGTH"] = str(max_content_length)

    logger.info(f"LLM日志系统已配置 - 控制台: {log_to_console}, 文件: {log_to_file}, 级别: {log_level}")


def get_llm_log_config():
    """获取当前LLM日志配置"""
    return {
        "include_request_content": os.getenv("LLM_LOG_INCLUDE_REQUEST", "false").lower() == "true",
        "include_response_content": os.getenv("LLM_LOG_INCLUDE_RESPONSE", "false").lower() == "true",
        "max_content_length": int(os.getenv("LLM_LOG_MAX_CONTENT_LENGTH", "200"))
    }


# 默认配置（如果需要）
def setup_default_logging():
    """设置默认的LLM日志配置"""
    setup_llm_logging(
        log_to_console=True,
        log_to_file=True,
        log_level="INFO",
        include_request_content=False,  # 不记录完整请求内容（可能很大）
        include_response_content=False,  # 不记录完整响应内容（可能很大）
        max_content_length=200  # 只记录前200个字符的预览
    )


if __name__ == "__main__":
    # 示例：如何使用配置
    setup_default_logging()

    logger.info("LLM日志配置已加载")
    logger.debug(f"当前配置: {get_llm_log_config()}")
