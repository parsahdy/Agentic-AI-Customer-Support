from .graph import build_graph
from .state import AgentState


class AgentService:

    def __init__(self):
        self.graph = build_graph()


    def run(self, question: str) -> AgentState:

        if not question or not question.strip():
            raise ValueError("Questioncannot be empty.")

        initial_state: AgentState = {
            "message": [],
            "question": question,
            "answer": "",
        }

        return self.graph.invoke(initial_state)