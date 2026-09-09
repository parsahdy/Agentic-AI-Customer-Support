from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field



class HumanReviewRequest(BaseModel):
    """
    Represents a request to involve a human operator.
    """

    request: str = Field(
        ...,
        min_length=1,
        description="The original user request.",
    )

    reason: str = Field(
        ...,
        min_length=1,
        description="Why human intervention is required.",
    )

    confidence_score: float | None = Field(
        default=None,
        ge=0.0,
        lt=1.0,
        description="Confidence score that triggered human review.",
    )

    operation: str | None = Field(
        default=None,
        description="Sensitive operation associated with the request.",
    )


class HumanDecision(BaseModel):
    """
    Represents the decision made by the human operator.
    """

    decision: Literal["approve", "reject", "escalate"] = Field(
        ...,
        description="Decision made by the human operator.",
    )


    comment: str | None = Field(
        default=None,
        description="Optional comment provided by the human operator",
    )


