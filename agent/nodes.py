import json
import re
import time

from typing import Callable

from langchain_core.messages import (
    ToolMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
)

from . import config
from .llm import create_llm, create_tool_llm
from .state import AgentState
from .router.router_factory import RouterFactory
from .tools.executor import ToolExecutor
from .tools.registry import ToolRegistry
from .memory.memory_service import MemoryService
from .errors.retry_policy import RetryPolicy
from .errors.error_policy import ErrorPolicy, RecoveryAction

from .human_loop.handler import HumanLoopHandler
from .human_loop.models import HumanReviewRequest
from .human_loop.policy import (
    CompositeHumanPolicy,
    LowConfidencePolicy,
    SensitiveOperationPolicy,
)

from knowledge_base.kb_service import KnowledgeBaseService
from evaluation import (
    RetrievalEvaluator, 
    FaithfulnessEvaluator, 
    ConfidenceEvaluator,
)

from langgraph.errors import GraphInterrupt


router = RouterFactory.create(config.ROUTER_TYPE)

human_policy = CompositeHumanPolicy(
    policies = [
        LowConfidencePolicy(),
        SensitiveOperationPolicy(),
    ]
)

human_loop_handler = HumanLoopHandler()
confidence_evaluator = ConfidenceEvaluator()


def wrap_node(
        node: Callable[[AgentState], dict],
        node_name: str,
        error_policy: ErrorPolicy,
        retry_policy: RetryPolicy,
        ) -> Callable[[AgentState], dict]:
    
    def wrapped(state: AgentState) -> dict:

        state["current_node"] = node_name
        state["status"] = "running"

        retry_count = 0

        while True:
            try:
                return node(state)

            except GraphInterrupt:
                raise InterruptedError(
                    "Agent workflow Interrupted."
                )
            
            except Exception as exc:
                print(
                    f"[ERROR] Node '{node_name}' failed: "
                    f"{type(exc).__name__}: {exc}"
                )
                action = error_policy.policy(exc, state)
                print(
                    f"[ERROR] Recovery action: {action}"
                )

                if action == RecoveryAction.RETRY:
                    if retry_count > retry_policy.max_retries:
                        print(
                            f"[ERROR] Node '{node_name}'"
                            f"reached maximum retry attempts."
                        )
                        return {
                            "status": "fail",
                            "error": {
                                "type": type(exc).__name__,
                                "message": str(exc),
                                "node": node_name,
                                "recovery_action": (
                                    "retry_exhausted"
                                ),
                                "retry_attempts": retry_count,
                            },
                        }
                    
                    retry_count += 1

                    delay = retry_policy.get_delay(retry_count)
                    time.sleep(delay)

                    continue

                if action == RecoveryAction.HUMAN_REVIEW:
                    return {
                        "status": "human_review",
                        "error": {
                            "type": type(exc).__name__,
                            "message": str(exc),
                            "node": node_name,
                            "recovery_action": (
                                RecoveryAction.HUMAN_REVIEW.value
                            ),
                            "retry_attempts": retry_count,
                        },
                    }

                return {
                    "status": "fail",
                    "error": {
                        "type": type(exc).__name__,
                        "message": str(exc),
                        "node": node_name,
                        "recovery_action": (
                            RecoveryAction.FAIL.value
                        ),
                        "retry_attempts": retry_count,
                    },
                }
                
    return wrapped


def Memory_loader(memory: MemoryService):
    def load_memory_node(state: AgentState) -> dict:

        user_id = state["user_id"]
        messages = state.get("messages", [])

        if not messages:
            return {
                "memory_context": []
            }

        latest_user_message = None

        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                latest_user_message = message
                break

        if latest_user_message is None:
            return {
                "memory_context": []
            }

        query = latest_user_message.content

        memories = memory.search_memories(
            user_id=user_id,
            query=query,
            limit=5,
        )

        memory_context = []

        for item in memories:
            memory_context.append({
                "key": item.key,
                "value": item.value,
            })

        return {
            "memory_context": memory_context,
        }

    return load_memory_node


def Memory_saver(memory: MemoryService):
    def save_memory_node(state: AgentState) -> dict:

        user_id = state["user_id"]
        messages = state.get("messages", [])

        if not messages: 
            return {}

        latest_user_message = None

        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                latest_user_message = message
                break

        if latest_user_message is None:
            return {}

        content = latest_user_message.content.strip()

        remember_patterns = {
            r"\bremember that\b", 
            r"\bremember\b", 
            r"\bdon't forget\b", 
            r"\bkeep in mind\b",
        }

        should_save = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in remember_patterns
        )

        if not should_save:
            return {}

        memory_text = re.sub(r"^\s*(remember that|remember|don't forget|keep in mind)\s*",
                            "", 
                            content, 
                            flags=re.IGNORECASE, ).strip()

        if not memory_text:
            return {}

        key = "user_preference"

        memory.save_memory(
            user_id=user_id,
            key=key,
            value={
                "content": memory_text,
            }
        )

        return {}

    return save_memory_node


def router_node(state: AgentState) -> dict:
    """
    Determine the route for the current query.
    """

    route = router.route(state)

    print(f"[DEBUG] Router returned: {route!r}")

    return {
        "route": route,
    }


def llm_node(state: AgentState) -> dict:
    """
    Generate an answer using the current conversation,
    memory, retrieved documents, and tool results.
    """

    llm = create_llm()

    query = state.get("query")

    conversation_history = list(
        state.get("messages", [])
    )

    memory_context = state.get(
        "memory_context",
        [],
    )

    retrieved_documents = state.get(
        "retrieved_documents",
        [],
    )

    tool_results = state.get(
        "tool_results",
        [],
    )

    context_parts: list[str] = []

    # Long-term memory
    if memory_context:

        memory_lines = []
        for memory in memory_context:
            
            value = memory.get("value", {})

            if isinstance(value, dict):
                content = value.get(
                    "content",
                    str(value),
                )
            else:
                content = str(value)

            memory_lines.append(
                f"- {content}"
            )

        context_parts.append(
            "Relevant long-term memories about the user:\n"
            + "\n".join(memory_lines)
        )


    # RAG context
    if retrieved_documents:
        document_lines = []

        for document in retrieved_documents:

            content = document.get("content", "")

            if content:
                document_lines.append(
                    content
                )

        if document_lines:
            context_parts.append(
                "Retrieved knowledge base context:\n"
                + "\n\n".join(document_lines)
            )

    # Tool results
    if tool_results:

        tool_lines = []

        for result in tool_results:
            tool_lines.append(
                str(result)
            )

        context_parts.append(
            "Results returned by tools:\n"
            + "\n".join(tool_lines)
        )

    context_message = None

    if context_parts:
        context_message = SystemMessage(
            content=(
                "Use the following information when answering "
                "the user's current request.\n\n"
                + "\n\n".join(context_parts)
            )
        )

    messages: list[BaseMessage] = []

    if context_message:
        messages.append(context_message)

    messages.extend(conversation_history)

    if not conversation_history:
        messages.append(
            HumanMessage(content=query)
        )

    elif not any(
        isinstance(message, HumanMessage)
        and message.content == query
        for message in conversation_history
    ):
        messages.append(
            HumanMessage(content=query)
        )

    response = llm.invoke(
        messages
    )

    print("[DEBUG] LLM response:", response)
    print(
        "[DEBUG] LLM response content:",
        response.content,
    )

    return {
        "messages": conversation_history + [response],
        "final_answer": response.content,
    }


def create_tool_call_node(registry: ToolRegistry):
    """
    Create a node that asks the LLM to generate tool calls.
    """

    llm = create_tool_llm(registry)

    def tool_call_node(state: AgentState) -> dict:
        """
        Generate tool calls for the current user request.
        """

        messages = list(state["messages"])
        response = llm.invoke(messages)   

        tool_calls = getattr(response, "tool_calls", [])

        if not tool_calls:
            return {
                "messages": [response],
                "tool_calls": [],
                "human_review_required": True,
                "human_review_request": {
                    "reason": "no proper tool found"
                }
            }

        return {
            "messages": [response],
            "tool_calls": tool_calls,
        }

    return tool_call_node


def create_tool_node(executor: ToolExecutor):
    """
    Create a tool node with its executor dependency injected.
    """

    def tool_node(state: AgentState) -> dict:
        """
        Execute the tools requested by the LLM.
        """

        tool_messages = []
        tool_results = []

        for tool_call in state["tool_calls"]:

            tool_name = tool_call["name"]
            arguments = tool_call.get("args", {})

            result = executor.execute(
                tool_name=tool_name,
                arguments=arguments,
            )

            tool_results.append(
                result.model_dump()
            )

            tool_messages.append(
                ToolMessage(
                    content=json.dumps(
                        tool_results[-1]["result"],
                        ensure_ascii=False,
                    ),
                    tool_call_id=tool_call["id"],
                )
            )

        return {
            "messages": tool_messages,
            "tool_results": tool_results,
        }

    return tool_node


def create_rag_node(
        kb: KnowledgeBaseService,
        retrieval_evaluator: RetrievalEvaluator,
    ):
    def rag_node(
            state: AgentState,
    ) -> dict:

        query = state["query"]

        retrieveds = kb.search(query)

        print("[DEBUG] retrieveds:", retrieveds)

        top1_score = retrieveds["top1_score"]
        mean_topk_score = retrieveds["mean_topk_score"]
        retrieval_score = retrieval_evaluator.evaluate(
            top1_score,
            mean_topk_score,
        )

        return {
            "retrieved_documents": retrieveds["retrieval_documents"],
            "top1_score": top1_score,
            "mean_topk_score": mean_topk_score,
            "retrieval_score": retrieval_score,
        }
    
    return rag_node
    

def create_evaluation_node(
    faithfulness_evaluator: FaithfulnessEvaluator,
    confidence_evaluator: ConfidenceEvaluator,
):

    def evaluation_node(state: AgentState):

        query = state.get("query")
        final_answer = state.get("final_answer")
        retrieved_documents = state.get("retrieved_documents")
        top1_score = state.get("top1_score")
        mean_topk_score = state.get("mean_topk_score")

        faithfulness_score = faithfulness_evaluator.evaluate(
            query=query,
            answer=final_answer,
            retrieved_contexts=retrieved_documents,
        )

        confidence_score = confidence_evaluator.calculate(
            top1_score=top1_score,
            mean_topk_score=mean_topk_score,
            faithfulness_score=faithfulness_score,
        )

        return {
            "faithfulness_score": faithfulness_score,
            "confidence_score": confidence_score,
        }

    return evaluation_node


def human_policy_node(state: AgentState) -> dict:

    if state.get("route") == "rag":
        confidence_score = state.get(
            "confidence_score"
        )
    else:
        confidence_score = None

    operation = None

    if state.get("tool_calls"):
        operation = state["tool_calls"][0].get("name")

    request = HumanReviewRequest(
        request=state["query"],
        reason="Human intervention evaluation.",
        confidence_score=confidence_score,
        operation=operation,
    )

    should_intervene = human_policy.should_intervene(
        request
    )

    return {
        "human_review_required": should_intervene,
        "human_review_request": (
            request.model_dump()
            if should_intervene
            else None
        ),
    }


def human_review_node(state: AgentState) -> dict:

    if not state.get("human_review_required"):
        return {}

    review_data = state.get("human_review_request")

    if review_data is None:
        raise ValueError(
            "Human review request is required."
        )

    request = HumanReviewRequest.model_validate(
        review_data
    )

    decision = human_loop_handler.request_human_decision(
        request
    )

    return {
        "human_decision": decision.model_dump()
    }
