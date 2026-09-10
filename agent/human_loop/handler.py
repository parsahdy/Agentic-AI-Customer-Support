from __future__ import annotations

from typing import Any

from langgraph.types import interrupt

from .models import HumanReviewRequest, HumanDecision
from .policy import HumanPolicy



class HumanLoopHandler:
    """
    Coordinates human intervention inside the workflow.

    The handler does not decide whether intervention is required.
    That responsibility belongs to HumanPolicy.

    The handler is responsible for:
    - creating the review payload
    - interrupting the workflow
    - validating the human decision
    """

    def __init__(self, policy: HumanPolicy) -> None:

        self.policy = policy
        

    def request_human_decision(self, request: HumanReviewRequest) -> HumanDecision:

        payload = {
            "type": "human_review",
            "request": request.model_dump(),
        }

        decision = interrupt(payload)

        return self._parse_decision(decision)


    @staticmethod
    def _parse_decision(decision: Any) -> HumanDecision:

        if isinstance(decision, HumanDecision):
            return decision

        if not isinstance(decision, dict):
            raise ValueError(
                "Human Decison must be a dictionary."
            )

        return HumanDecision.model_validate(decision)