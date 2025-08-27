import logging

import colorlog
from openai import OpenAI
from pydantic import BaseModel
from rich.pretty import pretty_repr


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


prompt = """
计算 1+1 等于多少

输出：{"content":"计算结果"}
"""


class ResponseModel(BaseModel):
    content: str


def test_with_vllm(vllm, response_model):
    setup_logging()

    client = OpenAI(
        api_key=vllm[1],
        base_url=vllm[0],
    )

    resp = client.beta.chat.completions.parse(
        model=vllm[2],
        response_format=response_model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    logging.info(f"final_resp=>{pretty_repr(resp)=}")
    print(pretty_repr(resp))
