from langgraph.graph import END, START, StateGraph

from .memory.memory_service import MemoryService
from .nodes import (
    create_tool_call_node,
    create_tool_node,
    human_policy_node,
    human_review_node,
    llm_node,
    load_memory_node,
    router_node,
    save_memory_node,
    rag_node,
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
    tool_call_node = create_tool_call_node(registry)
    tool_node = create_tool_node(executor)

    graph = StateGraph(AgentState)

    graph.add_node("load_memory",
                   lambda state: load_memory_node(state, memory))
    graph.add_node("router", router_node)
    graph.add_node("llm", llm_node)
    graph.add_node("rag",
                   lambda state: rag_node(state, kb))
    graph.add_node("tool_call", tool_call_node)
    graph.add_node("tool", tool_node)
    graph.add_node("human_policy", human_policy_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("save_memory",
                   lambda state: save_memory_node(state, memory))

    graph.add_edge(START, "load_memory")
    graph.add_edge("load_memory", "router")

    # Route selected by the Router
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
        }
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