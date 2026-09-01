import json
from langchain_core.messages import ToolMessage

from .llm import create_tool_llm
from .state import AgentState
from .router.router_factory import RouterFactory

from .tools.executor import ToolExecutor

from . import config


llm = create_tool_llm()
router = RouterFactory.create(config.ROUTER_TYPE)


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

    response = llm.invoke(
       state["messages"]
    )

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