import os

from langchain_openai import ChatOpenAI

from . import config
from .tools.registry import ToolRegistry


from dotenv import load_dotenv
load_dotenv()


def create_llm() -> ChatOpenAI:
    """
    Create and configure the LLM client.
    """

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is not set."
        )

    return ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=api_key,
        base_url=config.BASE_URL,
        temperature=config.TEMPERATURE,
    )


def create_tool_llm(registry: ToolRegistry | None = None) -> ChatOpenAI:
    llm = create_llm()

    registry = registry or ToolRegistry()

    return llm.bind_tools(registry.get_tools())