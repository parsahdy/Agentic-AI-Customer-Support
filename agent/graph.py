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
    create_evaluation_node,
)
from .state import AgentState
from .tools.executor import ToolExecutor
from .tools.registry import ToolRegistry
from .errors.retry_policy import RetryPolicy
from .errors.error_policy import ErrorPolicy
 
from knowledge_base.kb_service import KnowledgeBaseService
from evaluation import (
    RetrievalEvaluator, 
    FaithfulnessEvaluator, 
    ConfidenceEvaluator,
)



def has_failed(state: AgentState) -> bool:
    """
    True when a previous node stored an error (failure or an
    error-recovery request for human review).
    """

    return (
        state.get("error") is not None
        and state.get("status") in {"fail", "human_review"}
    )


def continue_unless_failed(next_node: str):
    """
    Build a router for a plain edge: go to `next_node`, or straight to
    `save_memory` when the previous node failed.
    """
 
    def route(state: AgentState) -> str:
        return "save_memory" if has_failed(state) else next_node
 
    return route


def route_after_router(state: AgentState) -> str:
    """
    Determine the next step after the router node.
    """
 
    if has_failed(state):
        return "save_memory"
 
    route = state.get("route")
 
    if route is None:
        raise ValueError(
            "Route is required after router node."
        )
 
    return route


def route_after_llm(state: AgentState) -> str:
    """
    Determine the next step after the LLM node.
    """
 
    if has_failed(state):
        return "save_memory"
 
    route = state.get("route")
 
    if route == "rag":
        return "evaluation"
 
    if route in {"direct", "tool"}:
        return "save_memory"
 
    raise ValueError(
        f"Unsupported route after LLM: {route!r}"
    )


def route_after_human_policy(state: AgentState) -> str:
    """
    Determine whether human review is required.
    """
 
    if has_failed(state):
        return "save_memory"
 
    if state.get("human_review_required"):
        return "human_review"
 
    else:
        if state.get("route") == "tool":
            return "tool"
        return "save_memory"


def route_after_human_review(state: AgentState) -> str:
    """
    Determine the next step after human review.
    """
 
    if has_failed(state):
        return "save_memory"
 
    decision = state.get("human_decision")
 
    if not decision:
        raise ValueError(
            "Human decision is required after human review."
        )
 
    decision_type = decision.get("decision")
 
    if decision_type == "approve":
        if state.get("route") == "tool":
            return "tool"
        return "save_memory"
 
    if decision_type in {"reject", "escalate"}:
        return "save_memory"
 
    raise ValueError(
        f"Unsupported human decision: {decision_type!r}"
    )


def build_graph(
    memory: MemoryService,
    registry: ToolRegistry,
    kb: KnowledgeBaseService,
    retrieval_evaluator: RetrievalEvaluator,
    faithfulness_evaluator: FaithfulnessEvaluator,
    confidence_evaluator: ConfidenceEvaluator,
    retry_policy: RetryPolicy,
    error_policy: ErrorPolicy,
):

    executor = ToolExecutor(registry, retry_policy)

    tool_call_node = create_tool_call_node(registry=registry)
    tool_node = create_tool_node(executor=executor)
    rag_node = create_rag_node(
        kb=kb,
        retrieval_evaluator=retrieval_evaluator,
    )
 
    load_memory_node = Memory_loader(memory=memory)
    save_memory_node = Memory_saver(memory=memory)
 
    evaluation_node = create_evaluation_node(
        faithfulness_evaluator=faithfulness_evaluator,
        confidence_evaluator=confidence_evaluator,
    ) 
 
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
        wrap_node(
            node = tool_node,
            node_name = "tool",
            error_policy = error_policy,
            retry_policy = retry_policy,
        ),
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
        "evaluation",
        wrap_node(
            node=evaluation_node,
            node_name="evaluation_node",
            error_policy=error_policy,
            retry_policy=retry_policy,
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

    graph.add_conditional_edges(
        "load_memory",
        continue_unless_failed("router"),
        {
            "router": "router",
            "save_memory": "save_memory",
        },
    )

    graph.add_conditional_edges(
        "router",
        route_after_router,
        {
            "direct": "llm",
            "rag": "rag",
            "tool": "tool_call",
            "save_memory": "save_memory",
        },
    )

    graph.add_conditional_edges(
        "rag",
        continue_unless_failed("llm"),
        {
            "llm": "llm",
            "save_memory": "save_memory",
        },
    )

    graph.add_conditional_edges(
        "evaluation",
        continue_unless_failed("human_policy"),
        {
            "human_policy": "human_policy",
            "save_memory": "save_memory",
        },
    )

    graph.add_conditional_edges(
        "tool_call",
        continue_unless_failed("human_policy"),
        {
            "human_policy": "human_policy",
            "save_memory": "save_memory",
        },
    )

    graph.add_conditional_edges(
        "human_policy",
        route_after_human_policy,
        {
            "human_review": "human_review",
            "tool": "tool",
            "save_memory": "save_memory",
        },
    )

    graph.add_conditional_edges(
        "tool",
        continue_unless_failed("llm"),
        {
            "llm": "llm",
            "save_memory": "save_memory",
        },
    )

    graph.add_conditional_edges(
        "llm",
        route_after_llm,
        {
            "evaluation": "evaluation",
            "save_memory": "save_memory",
        },
    )

    graph.add_conditional_edges(
        "human_review",
        route_after_human_review,
        {
            "tool": "tool",
            "save_memory": "save_memory",
        },
    )

    graph.add_edge("save_memory", END)
 
    return graph.compile(
        checkpointer=memory.get_checkpointer(),
        store=memory.get_store(),
    )