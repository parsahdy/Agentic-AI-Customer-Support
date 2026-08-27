from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):

    messages: Annotated[list[BaseMessage], add_messages]

    user_id: str
    session_id: str
    query: str

    retrieved_documents: list[dict]

    tool_calls: list[dict]
    tool_results: list[dict]


    final_answer: str
    error: str | None

    metadata: dict
