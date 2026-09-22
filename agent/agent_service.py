from .graph import build_graph
from .memory.memory_service import MemoryService
from .tools.registry import ToolRegistry
from .errors import RetryPolicy, ErrorPolicy

from knowledge_base.kb_service import KnowledgeBaseService


class AgentService:

    def __init__(
        self,
        memory: MemoryService | None = None,
        registry: ToolRegistry | None = None,
        kb: KnowledgeBaseService | None = None,
        retry_policy: RetryPolicy | None = None,
        error_policy: ErrorPolicy | None = None,
    ):

        self.memory = (
            memory
            if memory is not None
            else MemoryService()
        )

        self.registry = (
            registry
            if registry is not None
            else ToolRegistry()
        )

        self.kb = (
            kb
            if kb is not None
            else KnowledgeBaseService()
        )

        self.retry_policy = (
            retry_policy
            if retry_policy is not None
            else RetryPolicy()
        )

        self.error_policy = (
            error_policy
            if error_policy is not None
            else ErrorPolicy()
        )

        self.graph = build_graph(
            memory=self.memory,
            registry=self.registry,
            kb=self.kb,
            retry_policy=self.retry_policy,
            error_policy=self.error_policy,
        )

    def run(
        self,
        query: str,
        user_id: str,
        session_id: str,
    ):
        """
        Run the agent with a user query.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if not user_id:
            raise ValueError("user_id is required.")

        if not session_id:
            raise ValueError("session_id is required.")

        initial_state = {
            "messages": [
                {
                    "role": "user",
                    "content": query,
                }
            ],
            "user_id": user_id,
            "session_id": session_id,
            "query": query,
            "current_node": "",
            "retrieved_documents": [],
            "retrieval_score": 0.0,
            "top1_score": 0.0,
            "mean_topk_score": 0.0,
            "faithfulness_score": 0.0,
            "confidence_score": 0.0,
            "tool_calls": [],
            "tool_results": [],
            "iteration": 0,
            "max_iteration": 5,
            "final_answer": "",
            "error": {},
            "error_policy": "",
            "metadata": {},
            "route": None,
            "memory_context": [],
            "human_review_required": False,
            "human_review_request": {},
            "human_decision": {},
        }

        thread_id = f"{user_id}:{session_id}"

        config = {
            "configurable": {
                "thread_id": thread_id,
            }
        }

        return self.graph.invoke(
            initial_state,
            config=config,
        )

    def close(self) -> None:

        short_term = self.memory.short_term
        long_term = self.memory.long_term

        if hasattr(short_term, "close"):
            short_term.close()

        if hasattr(long_term, "close"):
            long_term.close()