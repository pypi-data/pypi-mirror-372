import logging

import colorlog
import pytest
from rich import print as rprint

from wujing.llm.exceptions import ConfigurationError, LLMCallError
from wujing.llm.llm_call import llm_call


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(levelname)s:%(name)s:%(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )
    logger.addHandler(handler)


def test_llm_call_with_azure_success(azure, response_model):
    """测试正常的 Azure LLM 调用"""
    messages = [
        {
            "role": "user",
            "content": "请简单介绍一下人工智能的发展历史。",
        },
    ]
    resp = llm_call(
        api_key=azure[1],
        api_version=azure[2],
        api_base=azure[0],
        model=azure[3],
        messages=messages,
        protocol="azure",
        cache_enabled=False,
    )
    rprint(f"{resp=}")

    resp_with_response_model = llm_call(
        api_key=azure[1],
        api_version=azure[2],
        api_base=azure[0],
        model=azure[3],
        messages=messages,
        response_model=response_model,
        protocol="azure",
        formatter="azure",
        cache_enabled=False,
    )
    rprint(f"{response_model.model_validate_json(resp_with_response_model)=}")


def test_llm_call_with_azure_invalid_api_key():
    """测试使用无效 API key 的异常情况"""
    messages = [
        {
            "role": "user",
            "content": "Hello, how are you?",
        },
    ]

    with pytest.raises(LLMCallError):
        llm_call(
            api_key="invalid_api_key",
            api_version="2025-04-01-preview",
            api_base="https://gpt5-rdg.openai.azure.com",
            model="gpt-5",
            messages=messages,
            protocol="azure",
            cache_enabled=False,
        )


def test_llm_call_with_azure_invalid_api_base():
    """测试使用无效 API base URL 的异常情况"""
    messages = [
        {
            "role": "user",
            "content": "Hello, how are you?",
        },
    ]

    with pytest.raises(LLMCallError):
        llm_call(
            api_key="some_api_key",
            api_version="2025-04-01-preview",
            api_base="https://invalid-url-that-does-not-exist.com",
            model="gpt-5",
            messages=messages,
            protocol="azure",
            cache_enabled=False,
        )


def test_llm_call_with_azure_missing_required_params():
    """测试缺少必需参数的异常情况"""
    messages = [
        {
            "role": "user",
            "content": "Hello, how are you?",
        },
    ]

    # 测试缺少 api_key
    with pytest.raises((ConfigurationError, LLMCallError, ValueError)):
        llm_call(
            api_version="2025-04-01-preview",
            api_base="https://gpt5-rdg.openai.azure.com",
            model="gpt-5",
            messages=messages,
            protocol="azure",
            cache_enabled=False,
        )

    # 测试缺少 api_version
    with pytest.raises((ConfigurationError, LLMCallError, ValueError)):
        llm_call(
            api_key="some_api_key",
            api_base="https://gpt5-rdg.openai.azure.com",
            model="gpt-5",
            messages=messages,
            protocol="azure",
            cache_enabled=False,
        )


def test_llm_call_with_azure_invalid_model():
    """测试使用无效模型名称的异常情况"""
    messages = [
        {
            "role": "user",
            "content": "Hello, how are you?",
        },
    ]

    with pytest.raises(LLMCallError):
        llm_call(
            api_key="some_api_key",
            api_version="2025-04-01-preview",
            api_base="https://gpt5-rdg.openai.azure.com",
            model="non_existent_model",
            messages=messages,
            protocol="azure",
            cache_enabled=False,
        )


def test_llm_call_with_azure_empty_messages():
    """测试空消息列表的异常情况"""
    with pytest.raises((ConfigurationError, LLMCallError, ValueError)):
        llm_call(
            api_key="some_api_key",
            api_version="2025-04-01-preview",
            api_base="https://gpt5-rdg.openai.azure.com",
            model="gpt-5",
            messages=[],
            protocol="azure",
            cache_enabled=False,
        )


def test_llm_call_with_azure_invalid_message_format():
    """测试无效消息格式的异常情况"""
    # 消息缺少必需的字段
    invalid_messages = [
        {
            "role": "user",
            # 缺少 content 字段
        },
    ]

    with pytest.raises((ConfigurationError, LLMCallError, ValueError)):
        llm_call(
            api_key="some_api_key",
            api_version="2025-04-01-preview",
            api_base="https://gpt5-rdg.openai.azure.com",
            model="gpt-5",
            messages=invalid_messages,
            protocol="azure",
            cache_enabled=False,
        )


def test_llm_call_with_azure_invalid_formatter(azure, response_model):
    """测试使用不兼容的 formatter 的异常情况"""
    messages = [
        {
            "role": "user",
            "content": "Hello, how are you?",
        },
    ]

    with pytest.raises((ConfigurationError, LLMCallError)):
        llm_call(
            api_key=azure[1],
            api_version=azure[2],
            api_base=azure[0],
            model=azure[3],
            messages=messages,
            response_model=response_model,
            protocol="azure",
            formatter="vllm",  # 使用不兼容的 formatter
            cache_enabled=False,
        )
