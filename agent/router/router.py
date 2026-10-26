from abc import ABC, abstractmethod
import re
 
from .. import config
from ..llm import create_llm
from ..prompts import router_prompt
from ..state import AgentState, Route
from .intent_detector import RouteDecision
from .intent_detector import KeywordIntentClassifier
 
from typing import cast
from typesafe_sdk import Choice, TypeSafeClient



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
        self.classifier = KeywordIntentClassifier()


    def route(self, state: AgentState) -> Route:

        query = state["query"]

        decision = self.classifier.classify(query)

        return decision.route

    

class LLMRouter(BaseRouter):

    def __init__(self):
        self.llm = create_llm(max_tokens=16)


    def route(self, state: AgentState) -> str:
        text = self.llm.invoke(router_prompt(state["query"])).content.strip().lower()

        match = re.search(r"\b(rag|tool|direct)\b", text)

        if match is None:
            raise ValueError(f"Router returned an unknown answer: {text!r}")

        return match.group(1)


class JevRouter(BaseRouter):
    """
    Route requests using JEV with an LLMRouter as fallback.
    """
 
    def __init__(
        self,
        confidence_threshold: float = 0.60,
        fallback_router: BaseRouter | None = None,
    ) -> None:
 
        self.client = TypeSafeClient(model=config.JEV_MODEL)
        self.confidence_threshold = confidence_threshold
        self.fall_back_router = (
            fallback_router
            if fallback_router is not None
            else LLMRouter()
        )
 
 
    def route(self, state: AgentState) -> Route:
 
        query = state["query"]
 
        result = self.client.system_one(
        state={
            "user_query": query,
            "knowledge_base_scope": [
                "internal product documentation",
                "company policies",
                "support knowledge base",
            ],
            "available_tools": [
                "get_order",
                "cancel_order",
                "create_ticket",
                "get_customer_info",
            ],
        },
        questions={
            "route": Choice(
                instructions=(
                    "Select exactly one route for `user_query`. "
                    "Classify based on the operation required, not only keywords."
                ),
                criteria={
                    "rag": (
                        "The request requires searching or grounding in the "
                        "application's private/internal knowledge base."
                    ),
                    "tool": (
                        "The request needs an external action or external/current "
                        "data through a tool, API, database, get_order, cancel_order, "
                        "create_ticket, get_customer_info, or similar capability."
                    ),
                    "direct": (
                        "General conversation or a question that can be answered "
                        "without the private knowledge base and without executing a tool."
                    ),
                },
            )
        },
    )
 
        answer = result.choices["route"]
 
        if answer.confidence < self.confidence_threshold:
            return self.fall_back_router.route(state)
 
        return cast(Route, answer.choice)
 
 
    def close(self) -> None:
        self.client.close()
    