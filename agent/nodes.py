from langchain_core.messages import HumanMessage

from .llm import create_llm
from .state import AgentState


llm = create_llm()

def llm_node(state: AgentState) -> dict:
    """
    Generate an answer using the LLM.
    """

    query = state["query"]

    response = llm.invoke(
        [HumanMessage(content=query)]
    )

    return {
        "messages": [response],
        "final_answer": response.content,
    }
