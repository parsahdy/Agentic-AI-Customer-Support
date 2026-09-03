import json
import re

from langchain_core.messages import ToolMessage, HumanMessage, SystemMessage

from .llm import create_tool_llm
from .state import AgentState
from .router.router_factory import RouterFactory
from .tools.executor import ToolExecutor
from .memory.memory_service import MemoryService

from . import config


llm = create_tool_llm()
router = RouterFactory.create(config.ROUTER_TYPE)


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

    memory_text = re.sub( r"^\s*(remember that|remember|don't forget|keep in mind)\s*",
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

    tool_calls = getattr(response, "tool_calls", [])

    return {
        "messages": [response],
        "tool_calls": tool_calls, 
        "final_answer": response.content,
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
                state=state,
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