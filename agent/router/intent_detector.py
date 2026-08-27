from typing import Literal

from pydantic import BaseModel

from .intents import INTENT_KEYWORDS
from ..state import Route



class RouteDecision(BaseModel):
    """
    Structured routing decision.
    """

    route: Route



class KeywordIntentClassifier:
    """
    Classifies user intent using predefined keywords.
    """

    def classify(self, query: str) -> RouteDecision:

        if not query or not query.strip():
            raise ValueError(
                "Query must be given."
            )

        query = query.lower().strip()

        for intent, keywords in INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in query:
                    return RouteDecision(route=intent)

        return RouteDecision(route="direct")
            