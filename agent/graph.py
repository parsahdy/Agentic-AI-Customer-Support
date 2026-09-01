from langgraph.graph import StateGraph, START, END

from .state import AgentState
from .nodes import (
    llm_node,
    create_tool_node
)

from .memory.memory_service import MemoryService
from .tools.registry import ToolRegistry
from .tools.executor import ToolExecutor


def route_after_llm(state: AgentState) -> str:
    """
    Decide whether the agent should execute tools
    or finish the current turn.
    """

    if state["iteration"] >= state["max_iteration"]:
        return "end"

    if state["tool_calls"]:
        return "tool"

    return "end"


def build_graph(memory: MemoryService,
                registry: ToolRegistry):

    executor = ToolExecutor(registry)
    tool_node = create_tool_node(executor)

    graph = StateGraph(AgentState)

    graph.add_node("llm", llm_node)
    graph.add_node("tool", tool_node)

    graph.add_edge(START, "llm")

    # Agent Loop
    graph.add_conditional_edges(
        "llm",
        route_after_llm,
        {
            "tool": "tool",
            "end": END,
        },
    )

    graph.add_edge("tool", "llm")

    return graph.compile(
        checkpointer=memory.get_checkpointer(),
        store=memory.get_store(),
    )