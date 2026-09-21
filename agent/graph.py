from langgraph.graph import END, START, StateGraph

from .memory.memory_service import MemoryService
from .nodes import (
    wrap_node,
    create_tool_call_node,
    create_tool_node,
    human_policy_node,
    human_review_node,
    llm_node,
    Memory_loader,
    router_node,
    Memory_saver,
    create_rag_node,
)
from .state import AgentState
from .tools.executor import ToolExecutor
from .tools.registry import ToolRegistry
from .errors.retry_policy import RetryPolicy

from knowledge_base.kb_service import KnowledgeBaseService



def route_after_router(state: AgentState) -> str:
    """
    Return the route selected by the router.
    """

    route = state.get("route")

    if route is None:
        raise ValueError(
            "Route is required after router node."
        )

    return route


def route_after_llm(state: AgentState) -> str:

    route = state.get("route")

    if route == "direct":
        return "save_memory"

    return "human_policy"


def route_after_human_policy(state: AgentState) -> str:
    """
    Determine whether human review is required.
    """

    if state.get("human_review_required"):
        return "human_review"

    return "save_memory"


def build_graph(
    memory: MemoryService,
    registry: ToolRegistry,
    retry_policy: RetryPolicy,
    kb: KnowledgeBaseService,
):

    executor = ToolExecutor(registry, retry_policy)

    tool_call_node = create_tool_call_node(registry=registry)
    tool_node = create_tool_node(executor=executor)
    rag_node = create_rag_node(kb=kb)

    load_memory_node = Memory_loader(memory=memory)
    save_memory_node = Memory_saver(memory=memory)

    graph = StateGraph(AgentState)

    graph.add_node(
        "load_memory",
        wrap_node(load_memory_node, "memory_loader"),
    )
    graph.add_node(
        "router",
        wrap_node(router_node, "router"),
    )
    graph.add_node(
        "llm",
        wrap_node(llm_node, "llm"),
    )
    graph.add_node(
        "rag",
        wrap_node(rag_node, "rag"),
    )
    graph.add_node(
        "tool_call",
        wrap_node(tool_call_node, "tool_call"),
    )
    graph.add_node(
        "tool",
        wrap_node(tool_node, "tool"),
    )
    graph.add_node(
        "human_policy",
        wrap_node(human_policy_node, "human_policy"),
    )
    graph.add_node(
        "human_review",
        wrap_node(human_review_node, "human_review"),
    )
    graph.add_node(
        "save_memory",
        wrap_node(save_memory_node, "memory_saver"),
    )

    graph.add_edge(START, "load_memory")
    graph.add_edge("load_memory", "router")

    graph.add_conditional_edges(
        "router",
        route_after_router,
        {
            "direct": "llm",
            "rag": "rag",
            "tool": "tool_call",
        },
    )

    graph.add_edge("rag", "llm")
    graph.add_edge("tool_call", "tool")
    graph.add_edge("tool", "llm")

    graph.add_conditional_edges(
        "llm",
        route_after_llm,
        {
            "save_memory": "save_memory",
            "human_policy": "human_policy",
        },
    )

    graph.add_conditional_edges(
        "human_policy",
        route_after_human_policy,
        {
            "human_review": "human_review",
            "save_memory": "save_memory",
        },
    )

    graph.add_edge("save_memory", END)

    return graph.compile(
        checkpointer=memory.get_checkpointer(),
        store=memory.get_store(),
    )