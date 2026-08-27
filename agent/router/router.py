from abc import ABC, abstractmethod

from ..state import AgentState, Route
from .intent_detector import KeywordIntentClassifier


class BaseRouter(ABC):
    """
    Abstraction for agent routing strategies.
    """

    @abstractmethod
    def route(self, state: AgentState) -> Route:
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

