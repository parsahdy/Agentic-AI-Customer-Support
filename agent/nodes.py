import json
import re
import time

from typing import Callable

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    BaseMessage,
)

from . import config
from .llm import create_llm, create_tool_llm
from .state import AgentState
from .prompts import build_system_prompt, tool_call_system_prompt
from .output_formatter import clean_answer
from .router.router_factory import RouterFactory
from .tools.executor import ToolExecutor
from .tools.registry import ToolRegistry
from .memory.memory_service import MemoryService
from .errors.retry_policy import RetryPolicy
from .errors.error_policy import ErrorPolicy, RecoveryAction
from .errors.error_classifier import ErrorClassifier, ErrorType

from .human_loop.handler import HumanLoopHandler
from .human_loop.models import (
    ToolHumanReviewRequest,
    RAGHumanReviewRequest,
)
from .human_loop.policy import (
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
fallback_router = RouterFactory.create("keyword")

rag_human_policy = LowConfidencePolicy()
tool_human_policy = SensitiveOperationPolicy()
human_loop_handler = HumanLoopHandler()
confidence_evaluator = ConfidenceEvaluator()


def wrap_node(
    node: Callable[[AgentState], dict],
    node_name: str,
    error_policy: ErrorPolicy,
    retry_policy: RetryPolicy,
) -> Callable[[AgentState], dict]:
    
    def wrapped(state: AgentState) -> dict:

        retry_count = 0

        while True:
            try:
                result = node(state) or {}

                return {
                    "current_node": node_name,
                    "status": "running",
                    **result,
                }

            except GraphInterrupt as interrupt:
                print(
                    f"[INTERRUPT] Node '{node_name}' interrupted: "
                    f"{type(interrupt).__name__}: {interrupt}"
                )
                raise
            
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
                    if retry_count >= retry_policy.max_retries:
                        print(
                            f"[ERROR] Node '{node_name}'"
                            f"reached maximum retry attempts."
                        )
                        return {
                            "current_node": node_name,
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
                        "current_node": node_name,
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
                    "current_node": node_name,
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


def _final_status(state: AgentState) -> str:
    """
    Final status of a finished run.
    """

    status = state.get("status")

    if status in {"fail", "human_review"} and state.get("error"):
        return status

    decision = state.get("human_decision") or {}

    if decision.get("decision") == "escalate":
        return "human_review"

    return "success"


def Memory_saver(memory: MemoryService):
    def save_memory_node(state: AgentState) -> dict:

        final_status = _final_status(state)

        user_id = state["user_id"]
        messages = state.get("messages", [])

        latest_user_message = None

        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                latest_user_message = message
                break

        if latest_user_message is None:
            return {"status": final_status}

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
            return {"status": final_status}

        memory_text = re.sub(
            r"^\s*(remember that|remember|don't forget|keep in mind)\s*",
            "", 
            content, 
            flags=re.IGNORECASE,
        ).strip()

        if not memory_text:
            return {"status": final_status}

        key = "user_preference"

        memory.save_memory(
            user_id=user_id,
            key=key,
            value={
                "content": memory_text,
            }
        )

        return {"status": final_status}

    return save_memory_node


def router_node(state: AgentState) -> dict:
    """
    Determine the route for the current query.

    Transient errors (rate limit, timeout...) are re-raised so that the
    retry logic of wrap_node can handle them. For any other failure of the
    main router (for example an invalid structured output) the keyword
    router is used, so the graph never reaches the conditional edge
    without a route.
    """

    try:
        route = router.route(state)

    except Exception as exc:
        classified = ErrorClassifier.classify(exc)

        if classified["error_type"] == ErrorType.TRANSIENT:
            raise

        print(
            f"[WARNING] Main router failed "
            f"({type(exc).__name__}: {exc}). "
            f"Using the keyword router as fallback."
        )

        route = None

    if route not in {"rag", "tool", "direct"}:
        route = fallback_router.route(state)

    print(f"[DEBUG] Router returned: {route!r}")

    return {
        "route": route,
    }


def _conversation_history(state: AgentState) -> list[BaseMessage]:
    """
    Plain user / assistant turns of the conversation.

    Tool calls and tool results are NOT part of the history. They travel
    through state["tool_calls"] / state["tool_results"] and are given to
    the LLM as context, so the history never contains a dangling tool call
    (e.g. after a human reviewer rejected the operation).
    """

    return [
        message
        for message in state.get("messages", [])
        if isinstance(message, HumanMessage)
        or (
            isinstance(message, AIMessage)
            and not message.tool_calls
            and message.content
        )
    ]


def llm_node(state: AgentState) -> dict:
    """
    Generate an answer using the current conversation,
    memory, retrieved documents, and tool results.
    """

    llm = create_llm()

    query = state.get("query")
    route = state.get("route")

    conversation_history = _conversation_history(state)

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
    if route == "rag":
        document_lines = [
            document.get("content", "")
            for document in retrieved_documents
            if document.get("content")
        ]

        if document_lines:
            context_parts.append(
                "Retrieved knowledge base context:\n"
                + "\n\n".join(
                    f"[Document {index}]\n{content}"
                    for index, content in enumerate(
                        document_lines, start=1
                    )
                )
            )
        else:
            context_parts.append(
                "Retrieved knowledge base context:\n"
                "(no relevant documents were retrieved)"
            )

    # Tool results
    if tool_results:

        tool_lines = [
            json.dumps(result, ensure_ascii=False, default=str)
            for result in tool_results
        ]

        context_parts.append(
            "Results returned by tools:\n"
            + "\n".join(tool_lines)
        )

    system_prompt = build_system_prompt(route)

    if context_parts:
        system_prompt += (
            "\n\nUse the following information when answering "
            "the user's current request.\n\n"
            + "\n\n".join(context_parts)
        )

    messages: list[BaseMessage] = [
        SystemMessage(content=system_prompt)
    ]

    messages.extend(conversation_history)

    if not any(
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

    truncated = (
        response.response_metadata.get("finish_reason") == "length"
    )

    answer = clean_answer(response.content, truncated=truncated)

    return {
        "messages": [AIMessage(content=answer)],
        "final_answer": answer,
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

        if state.get("route") != "tool":
            return {
                "tool_calls": [],
                "status": "fail",
                "error": {
                    "type": "InvalidRouteError",
                    "message": (
                        "Tool call node was invoked without "
                        "the 'tool' route."
                    ),
                },
            }

        messages: list[BaseMessage] = [
            SystemMessage(content=tool_call_system_prompt()),
            *_conversation_history(state),
        ]

        response = llm.invoke(messages)

        tool_calls = getattr(response, "tool_calls", [])

        print("[DEBUG] Tool Calls:", tool_calls)

        if not tool_calls:
            return {
                "tool_calls": [],
                "final_answer": response.content or "",
                "status": "fail",
                "error": {
                    "type": "ToolCallGenerationError",
                    "message": (
                        "The LLM did not generate any tool calls."
                    ),
                },
            }

        return {
            "tool_calls": tool_calls,
            "status": "running",
            "error": None,
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

        return {
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

        top1_score = min(max(retrieveds["top1_score"], 0.0), 1.0)
        mean_topk_score = min(
            max(retrieveds["mean_topk_score"], 0.0), 1.0
        )
        retrieval_score = retrieval_evaluator.evaluate(
            top1_score,
            mean_topk_score,
        )

        return {
            "retrieval_performed": True,
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

        retrieved_contexts = [
            document["content"]
            for document in (retrieved_documents or [])
            if document.get("content")
        ]

        if not retrieved_contexts:
            return {
                "faithfulness_score": 0.0,
                "confidence_score": 0.0,
            }

        faithfulness_score = faithfulness_evaluator.evaluate(
            query=query,
            answer=final_answer,
            retrieved_contexts=retrieved_contexts,
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
    """
    Decide whether human intervention is required
    based on current workflow route.
    """

    route = state.get("route")

    if route == "rag":
        request = RAGHumanReviewRequest(
            request=state["query"],
            reason=(
                "Human intervention required because "
                "the RAG confidence score is below the "
                "configured threshold."
            ),
            confidence_score=state.get(
                "confidence_score"
            ),
            retrieved_documents=state.get(
                "retrieved_documents",
                [],
            ),
            generated_answer=state.get(
                "final_answer"
            ),  
        )

        should_intervene = rag_human_policy.should_intervene(
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

    elif route == "tool":

        tool_calls = state.get(
            "tool_calls",
            []
        )

        sensitive_operations: list[dict] = []

        for tool_call in tool_calls:

            operation = tool_call.get("name")
            arguments = tool_call.get("args", {})

            single_request = ToolHumanReviewRequest(
                request=state["query"],
                reason="Sensitive tool operation.",
                operation=operation,
                arguments=arguments,
            )

            if tool_human_policy.should_intervene(single_request):
                sensitive_operations.append(
                    {
                        "name": operation,
                        "arguments": arguments,
                    }
                )

        if sensitive_operations:

            names = ", ".join(
                item["name"] for item in sensitive_operations
            )

            request = ToolHumanReviewRequest(
                request=state["query"],
                reason=(
                    "Human intervention required because "
                    f"the requested tool operation(s) are sensitive: "
                    f"{names}."
                ),
                operation=sensitive_operations[0]["name"],
                arguments=sensitive_operations[0]["arguments"],
                sensitive_operations=sensitive_operations,
            )

            return {
                "human_review_required": True,
                "human_review_request": request.model_dump(),
            }

        return {
            "human_review_required": False,
            "human_review_request": None,
        }

    return {
        "human_review_required": False,
        "human_review_request": None,
    }


def human_review_node(state: AgentState) -> dict:
    """
    Interrupt the workflow and request human intervention.

    When the workflow is resumed through LangGraph,
    the interrupt call returns the human decision.
    """

    if not state.get("human_review_required"):
        return {}

    review_data = state.get("human_review_request")

    if review_data is None:
        raise ValueError(
            "Human review request is required."
        )

    route = state.get("route")

    if route == "rag":
        request = RAGHumanReviewRequest.model_validate(
            review_data
        )

    elif route == "tool":
        request = ToolHumanReviewRequest.model_validate(
            review_data
        )

    else:
        raise ValueError(
            f"Unsupported route for human review: {route!r}"
        )

    decision = human_loop_handler.request_human_decision(
        request
    )

    update = {
        "human_decision": decision.model_dump()
    }

    if decision.decision == "reject":
        update["final_answer"] = (
            "Your request was reviewed by a human agent and could not "
            "be approved, so no action was taken."
        )

    elif decision.decision == "escalate":
        update["final_answer"] = (
            "Your request has been escalated to a human agent, who will "
            "follow up with you. No action has been taken yet."
        )

    return update