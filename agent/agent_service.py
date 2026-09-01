from .graph import build_graph
from .memory.memory_service import MemoryService
from .tools.registry import ToolRegistry



class AgentService:

    def __init__(self, memory: MemoryService | None=None):

        self.memory = memory or MemoryService()
        self.registry = ToolRegistry()
        self.graph = build_graph(
            memory=self.memory,
            registry=self.registry,
        )


    def run(self, 
            query: str,
            user_id: str,
            session_id: str):
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
            "retrieved_documents": [],
            "tool_calls": [],
            "tool_results": [],
            "iteration": 0,
            "max_iteration": 5,
            "final_answer": "",
            "error": None,
            "metadata": {},
            "route": None
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