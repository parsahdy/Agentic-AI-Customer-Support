from langchain_core.messages import HumanMessage

from .llm import create_llm
from .state import AgentState
from router.router_factory import RouterFactory

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

    return {
        "messages": [response],
        "final_answer": response.content,
    }


