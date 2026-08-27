from langgraph.graph import StateGraph, START, END

from .state import AgentState
from .nodes import llm_node


def build_graph():
    """
    Build and compile the agent workflow.
    """

    graph = StateGraph(AgentState)

    graph.add_node("llm", llm_node)

    graph.add_edge(START, "llm")
    graph.add_edge("llm", END)

    return graph.compile()