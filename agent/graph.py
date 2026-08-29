from langgraph.graph import StateGraph, START, END

from .state import AgentState
from .nodes import llm_node, tool_node



def route_after_llm(state: AgentState) -> str:

    if state["iteration"] >= state["max_iteration"]:
        return "end"

    if state["tool_calls"]:
        return "tool"

    return "end"


def build_graph():
    """
    Build and compile the agent workflow.
    """

    graph = StateGraph(AgentState)

    graph.add_node("llm", llm_node)
    graph.add_node("tool", tool_node)

    graph.add_edge(START, "llm")

    graph.add_conditional_edges(
        "llm",
        route_after_llm,
        {
            "tool": "tool",
            "end": END,
        },
    )

    graph.add_edge("tool", "llm")

    return graph.compile()