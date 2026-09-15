import json
import re

from langchain_core.messages import (
    ToolMessage,
    HumanMessage,
    SystemMessage,
)

from . import config
from .llm import create_llm, create_tool_llm
from .state import AgentState
from .router.router_factory import RouterFactory
from .tools.executor import ToolExecutor
from .tools.registry import ToolRegistry
from .memory.memory_service import MemoryService

from .human_loop.handler import HumanLoopHandler
from .human_loop.models import HumanReviewRequest
from .human_loop.policy import (
    CompositeHumanPolicy,
    LowConfidencePolicy,
    SensitiveOperationPolicy,
)

from evaluation.confidence.confidence_evaluator import ConfidenceEvaluator
from knowledge_base.kb_service import KnowledgeBaseService


router = RouterFactory.create(config.ROUTER_TYPE)

human_policy = CompositeHumanPolicy(
    policies = [
        LowConfidencePolicy(),
        SensitiveOperationPolicy(),
    ]
)

human_loop_handler = HumanLoopHandler()
confidence_evaluator = ConfidenceEvaluator()



def load_memory_node(state: AgentState,
                     memory: MemoryService) -> dict:

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


def save_memory_node(state: AgentState,
                     memory: MemoryService) -> dict:

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


def router_node(state: AgentState) -> dict:
    """
    Determine the route for the current query.
    """

    route = router.route(state)

    return {
        "route": route,
    }


def llm_node(state: AgentState) -> dict:
    """
    Generate a direct answer using the LLM.
    """

    llm = create_llm()

    messages = list(state["messages"])

    memory_context = state.get(
        "memory_context",
        [],
    )

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

        memory_message = SystemMessage(
            content=(
                "Relevent long-term memories about the user:\n"
                + "\n".join(memory_lines)
                + "\n\n"
                "use these memories only when they are relevent"
                "to the current request."
            )
        )

        messages.insert(
            0,
            memory_message
        )


    response = llm.invoke(messages)

    return {
        "messages": [response],
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

        return {
            "messages": [response],
            "tool_calls": tool_calls,
        }

    return tool_call_node


def rag_node(
        state: AgentState,
        kb: KnowledgeBaseService
) -> dict:

    query = state["query"]

    retrieved_documents = kb.search(query)

    return {
        "retrieved_documents": retrieved_documents,
    }
    

def confidence_evaluation_node(
        state: AgentState) -> dict:

    top1_score = state.get("top1_score")
    mean_topk_score = state.get("mean_topk_score")
    faithfilness_score = state.get("faithfulness_score")

    if (
        top1_score is None
        or mean_topk_score is None
        or faithfilness_score is None
    ):
        return {
            "confidence_score": None,
        }

    confidence_score = confidence_evaluator.calculate(
        top1_score=top1_score,
        mean_topk_score=mean_topk_score,
        faithfulness_score=faithfilness_score,
    )

    return {
        "confidence_score": confidence_score,
    }


def human_policy_node(state: AgentState) -> dict:

    confidence_score = state.get(
        "confidence_score"
    )

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

            tool_results.append({
                "tool_name": tool_name,
                "result": result.model_dump(),
            })

            tool_messages.append(
                ToolMessage(
                    content=json.dumps(
                        result.model_dump(),
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