from abc import ABC, abstractmethod

from ..llm import create_llm
from ..state import AgentState, Route
from .intent_detector import RouteDecision
from .intents import INTENT_KEYWORDS
from .intent_detector import KeywordIntentClassifier


class BaseRouter(ABC):
    """
    Abstraction for agent routing strategies.
    """

    @abstractmethod
    def route(self, state: AgentState) -> str:
        """
        Determine the next route from the current agent state.
        """
        pass



class KeywordRouter(BaseRouter):
    """
    Route requests using keyword-based intent classification.
    """

    def __init__(self):
        self.classifier = KeywordIntentClassifier


    def route(self, state: AgentState) -> Route:

        query = state["query"]

        decision = self.classifier.classify(query)

        return decision.route

    

class LLMRouter(BaseRouter):

    def __init__(self):
        self.llm = create_llm().with_structured_output(
            RouteDecision
        )


    def route(self, state: AgentState) -> str:

        query = state["query"]

        decision: RouteDecision = self.llm.invoke(
            f"""
            Classify the user's query into exactly one route.

            Routes:
            - rag: questions that can be answered using the knowledge base
            - tool: requests that require an external tool or action
            - direct: general conversation or questions that need neither RAG nor tools

            User query:
            {query}
            """
        )

        return decision.route