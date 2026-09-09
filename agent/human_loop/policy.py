from __future__ import annotations

import re
from abc import ABC, abstractmethod

from .models import HumanReviewRequest



class HumanPolicy(ABC):
    """
    Base strategy for deciding whether human intervention is required.
    """

    @abstractmethod
    def should_intervene(self, request: HumanReviewRequest) -> bool:
        class HumanPolicy(ABC):
            """
            Base strategy for deciding whether human intervention is required.
            """

            raise NotImplementedError


class LowConfidencePolicy(HumanPolicy):
    """
    Requests human intervention when confidence is below
    the configured threshold.
    """

    def __init__(self, review_threshold = 0.6) -> None:

        if not 0.0 <= review_threshold <= 1.0:
            raise ValueError(
                "review_threshold must be between 0 and 1."
            )

        self.review_threshold = review_threshold


    def should_intervene(self, request: HumanReviewRequest) -> bool:

        if request.confidence_score is None:
            return True

        return request.confidence_score < self.review_threshold


class SensitiveOperationPolicy(HumanPolicy):
    """
    Requests human intervention when confidence is below
    the configured threshold.
    """
 
    DEFAULT_PATTERNS = (
        r"\bcancel\b.*\border\b",
        r"\bdelete\b",
        r"\brefund\b",
        r"\bchargeback\b",
        r"\bclose\b.*\baccount\b",
        r"\bchange\b.*\bpayment\b",
    )

    def __init__(self, patterns: tuple[str, ...] | None = None) -> None:

        self.patterns = patterns or self.DEFAULT_PATTERNS


    def should_intervene(self, request: HumanReviewRequest) -> bool:

        content = request.request

        return any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.patterns
        )


class CompositeHumanPolicy(HumanPolicy):
    """
    Requests human intervention for sensitive operations.
    """

    def __init__(self, policies: list[HumanPolicy]) -> None:

        if not policies:
            raise ValueError(
                "At least one human policy is required."
            )

        self.policies = policies


    def should_intervene(self, request: HumanReviewRequest) -> bool:

        return any(
            policy.should_intervene(request)
            for policy in self.policies
        )
        
