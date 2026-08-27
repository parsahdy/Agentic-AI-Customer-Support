from langchain_core.messages import HumanMessage

from .graph import build_graph
from .state import AgentState


class AgentService:

    def __init__(self):
        self.graph = build_graph()


    def run(self, query: str) -> AgentState:
        """
        Run the agent with a user query.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        initial_state: AgentState = {
            "messages": [
                HumanMessage(content=query)
            ],
            "user_id": "",
            "session_id": "",
            "query": query,
            "retrieved_documents": [],
            "tool_calls": [],
            "tool_results": {},
            "final_answer": "",
            "error": None,
            "metadata": {},
            "route": None
        }

        return self.graph.invoke(initial_state)