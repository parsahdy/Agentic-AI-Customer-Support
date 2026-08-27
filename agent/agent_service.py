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
            raise ValueError("Questioncannot be empty.")

        initial_state: AgentState = {
            "messages": [],
            "query": query,
            "user_id": "",
            "session_id": "",
            "retrieved_documents": [],
            "tool_calls": [],
            "tool_results": {},
            "final_answer": "",
            "error": None,
            "metadata": {},
        }

        return self.graph.invoke(initial_state)