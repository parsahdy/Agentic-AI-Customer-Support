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

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "API_KEY is not set."
        )

    return ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=api_key,
        base_url=config.BASE_URL,
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS,
        model_kwargs={
            "reasoning_effort": "none",
        },
    )


def create_tool_llm(registry: ToolRegistry | None = None) -> ChatOpenAI:

    llm = create_llm(max_tokens=100)

    return llm.bind_tools(registry.get_tools())