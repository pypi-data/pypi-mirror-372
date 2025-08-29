import logging

import colorlog
from rich import print as rprint

from wujing.llm.llm_call import llm_call


def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.TRACE)

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


prompt = """
计算 1+1 等于多少

输出：{"content":"计算结果"}
"""


def test_llm_call_with_openai_vllm(vllm, messages, response_model, context):
    resp_with_response_model = llm_call(
        api_key=vllm[1],
        api_base=vllm[0],
        model=vllm[2],
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        response_model=response_model,
        context=context,
        protocol="openai",
        formatter="vllm",
        cache_enabled=False,
    )
    rprint(f"{response_model.model_validate_json(resp_with_response_model)=}")
