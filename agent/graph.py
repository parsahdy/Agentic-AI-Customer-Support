from langgraph.graph import StateGraph, START, END

from .state import AgentState
from .nodes import (
    llm_node, 
    router_node, 
    create_tool_node, 
    load_memory_node, 
    save_memory_node,
)

from .memory.memory_service import MemoryService
from .tools.registry import ToolRegistry
from .tools.executor import ToolExecutor


def route_after_llm(state: AgentState) -> str:

    if state.get("tool_calls"):
        return "tool"

    return "save_memory"


def build_graph(memory: MemoryService,
                registry: ToolRegistry):

    executor = ToolExecutor(registry)
    tool_node = create_tool_node(executor)

    graph = StateGraph(AgentState)

    graph.add_node("load_memory",
                   lambda state: load_memory_node(state, memory))
    graph.add_node("llm", llm_node)
    graph.add_node("tool", tool_node)
    graph.add_node("save_memory",
                   lambda state: save_memory_node(state, memory))

    graph.add_edge(START, "load_memory")
    graph.add_edge("load_memory", "llm")

    # Agent Loop
    graph.add_conditional_edges(
        "llm",
        route_after_llm,
        {
            "tool": "tool",
            "save_memory": "save_memory",
        },
    )

    graph.add_edge("tool", "llm")
    graph.add_edge("save_memory", END)

    return graph.compile(
        checkpointer=memory.get_checkpointer(),
        store=memory.get_store(),
    )