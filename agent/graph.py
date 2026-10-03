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



def route_after_router(state: AgentState) -> str:
    """
    Determine the next step after the router node.
    """

    route = state.get("route")

    print(f"[DEBUG] State route after router: {route!r}")

    if route is None:
        raise ValueError(
            "Route is required after router node."
        )

    print(
        f"[DEBUG] route_after_router | "
        f"error={state.get('error')!r} | "
        f"route={state.get('route')!r}"
    )

    return route


def route_after_llm(state: AgentState) -> str:
    """
    Determine the next step after the LLM node.
    """

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
    graph.add_edge("evaluation", "human_policy")
    graph.add_edge("tool_call", "human_policy")

    graph.add_conditional_edges(
        "human_policy",
        route_after_human_policy,
        {
            "human_review": "human_review",
            "tool": "tool",
            "save_memory": "save_memory",
        },
    )
    
    graph.add_edge("tool", "llm")

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