from langchain_core.messages import HumanMessage

from .llm import create_llm
from .state import AgentState


llm = create_llm()


def llm_node(state: AgentState) -> dict:
    question = state["question"]

    response = llm.invoke(
        [HumanMessage(content=question)]
    )

    return {
        "message": [response],
        "answer": response.content,
    }
