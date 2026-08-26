import os

from langchain_openai import ChatOpenAI

from . import config


def create_llm() -> ChatOpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is not set."
        )

    return ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=api_key,
        base_url=config.BASE_URL,
        temperature=config.TEMPERATURE
    )