from langgraph.graph import StateGraph, START, END

from .state import AgentState
from .nodes import llm_node, router_node



def route_after_decision(state: AgentState) -> str:
    """
    Select the next node based on the routing decision.
    """

    route = state["route"]

    if route is None:
        raise ValueError("Route has not been determined.")

    return route


def build_graph():
    """
    Build and compile the agent workflow.
    """

    graph = StateGraph(AgentState)

    graph.add_node("decision", router_node)

    # Temporary nodes.
    # These will be replaced by real RAG and Tool nodes
    # in later sprints.
    graph.add_node("rag", llm_node)
    graph.add_node("tool", llm_node)
    graph.add_node("direct", llm_node)

    graph.add_conditional_edges(
        "decision",
        route_after_decision,
        {
            "rag": "rag",
            "tool": "tool",
            "direct": "direct",
        }
    )

    graph.add_edge("rag", END)
    graph.add_edge("tool", END)
    graph.add_edge("direct", END)

    return graph.compile()