from typing import TypedDict, Annotated, Literal, Any

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from . import config


Route = Literal["rag", "tool", "direct"]

class AgentState(TypedDict):
    """
    Runtime state shared between agent nodes.
    """

    messages: Annotated[list[BaseMessage], add_messages]

    user_id: str
    session_id: str
    query: str

    retrieved_documents: list[dict]

    tool_calls: list[dict]
    tool_results: list[dict]

    iteration: int
    max_iteration: int = config.MAX_ITERATIONS

    final_answer: str
    error: str | None

    metadata: dict

    route: Route | None

    memory_context: list[dict[str, Any]]
