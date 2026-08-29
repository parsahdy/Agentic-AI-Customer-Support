import os

from langchain_openai import ChatOpenAI

from . import config
from .tools.registry import ToolRegistry


def create_llm() -> ChatOpenAI:
    """
    Create and configure the LLM client.
    """

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is not set."
        )

    llm = ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=api_key,
        base_url=config.BASE_URL,
        temperature=config.TEMPERATURE,
    )

    tools = ToolRegistry.get_tools()

    return llm.bind_tools(tools)