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
from .errors.error_policy import ErrorPolicy

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


def route_after_error_policy(state: AgentState) -> str:
    """
    Return the route selected by error policy.
    """

    return state.get("error_policy")



def build_graph(
    memory: MemoryService,
    registry: ToolRegistry,
    retry_policy: RetryPolicy,
    error_policy: ErrorPolicy,
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
        wrap_node(
            node = load_memory_node, 
            node_name = "memory_loader",
            error_policy = error_policy,
            retry_policy = retry_policy,
        ),
    )
    graph.add_node(
        "router",
        wrap_node(
            node = router_node, 
            node_name = "router",
            error_policy = error_policy,
            retry_policy = retry_policy,
        ),
    )
    graph.add_node(
        "llm",
        wrap_node(
            node = llm_node, 
            node_name = "llm",
            error_policy = error_policy,
            retry_policy = retry_policy,
        ),
    )
    graph.add_node(
        "rag",
        wrap_node(
            node = rag_node, 
            node_name = "rag",
            error_policy = error_policy,
            retry_policy = retry_policy,
        ),
    )
    graph.add_node(
        "tool_call",
       wrap_node(
            node = tool_call_node, 
            node_name = "tool_call",
            error_policy = error_policy,
            retry_policy = retry_policy,
        ),
    )
    graph.add_node(
        "tool",
        tool_node
    )
    graph.add_node(
        "human_policy",
        wrap_node(
            node = human_policy_node, 
            node_name = "human_policy",
            error_policy = error_policy,
            retry_policy = retry_policy,
        ),
    )
    graph.add_node(
        "human_review",
        wrap_node(
            node = human_review_node, 
            node_name = "human_review",
            error_policy = error_policy,
            retry_policy = retry_policy,
        ),
    )
    graph.add_node(
        "save_memory",
        wrap_node(
            node = save_memory_node, 
            node_name = "save_memory",
            error_policy = error_policy,
            retry_policy = retry_policy,
        ),
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