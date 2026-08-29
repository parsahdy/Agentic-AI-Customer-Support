import json
from langchain_core.messages import ToolMessage

from .llm import create_llm
from .state import AgentState
from router.router_factory import RouterFactory

from tools.executor import ToolExecutor


from . import config


llm = create_llm()
router = RouterFactory.create(config.ROUTER_TYPE)


def router_node(state: AgentState) -> dict:
    """
    Determine the route for the current query.
    """

    route = router.route(state)

    return {
        "router": route,
    }


def llm_node(state: AgentState) -> dict:
    """
    Generate a direct answer using the LLM.
    """

    response = llm.invoke(
       state["messages"]
    )

    tool_calls = getattr(response, "tool_calls", [])

    return {
        "messages": [response],
        "tool_calls": tool_calls, 
        "final_answer": response.content,
    }


def tool_node(state: AgentState) -> dict:

    tool_messages = []
    tool_results = []

    for tool_call in state["tool_calls"]:

        tool_name = tool_call["name"]
        arguments = tool_call.get("args_schema", {})

        result = ToolExecutor.execute(
            tool_name=tool_name,
            arguments=arguments,
            state=state,
        )

        tool_results.append({
            "tool_name": tool_name,
            "result": result,
        })

        tool_messages.append(
            ToolMessage(
                content=json.dumps(result),
                tool_call_id=tool_call["id"],
            )
        )

    return {
        "messages": tool_messages,
        "tool_results": tool_results,
    }
    