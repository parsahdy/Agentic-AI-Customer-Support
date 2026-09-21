from typing import TypedDict, Annotated, Literal, Any

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


Route = Literal["rag", "tool", "direct"]


class AgentState(TypedDict):
    """
    Runtime state shared between agent nodes.
    """

    messages: Annotated[list[BaseMessage], add_messages]

    current_node: str

    user_id: str
    session_id: str
    query: str

    retrieved_documents: list[dict]

    retrieval_score: float | None
    top1_score: float | None
    mean_topk_score: float | None

    faithfulness_score: float | None
    confidence_score: float | None

    tool_calls: list[dict]
    tool_results: list[dict]

    iteration: int
    max_iteration: int

    final_answer: str
    error: dict[str, Any] | None

    metadata: dict[str, Any]

    route: Route | None

    memory_context: list[dict[str, Any]]

    human_review_required: bool
    human_review_request: dict[str, Any] | None
    human_decision: dict[str, Any] | None
