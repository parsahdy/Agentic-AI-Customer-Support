from __future__ import annotations

import re
from abc import ABC, abstractmethod

from .models import (
    ToolHumanReviewRequest,
    RAGHumanReviewRequest,
)


class HumanPolicy(ABC):
    """
    Base strategy for deciding whether human intervention is required.
    """

    @abstractmethod
    def should_intervene(
        self, 
        request: object
    ) -> bool:
        """
        Determine whether human intervention is required.
        """

        raise NotImplementedError


class LowConfidencePolicy(HumanPolicy):
    """
    Requests human intervention when confidence is below
    the configured threshold.
    """

    def __init__(
        self,
        review_threshold: float = 0.6
    )-> None:

        if not 0.0 <= review_threshold <= 1.0:
            raise ValueError(
                "review_threshold must be between 0 and 1."
            )

        self.review_threshold = review_threshold


    def should_intervene(
        self,
        request: RAGHumanReviewRequest
    ) -> bool:

        if request.confidence_score is None:
            return False

        return request.confidence_score < self.review_threshold


class SensitiveOperationPolicy(HumanPolicy):
    """
    Requests human intervention for sensitive tool operations.
    """
 
    DEFAULT_PATTERNS = (
        r"\bcancel\b.*\border\b",
        r"\bdelete\b",
        r"\brefund\b",
        r"\bchargeback\b",
        r"\bclose\b.*\baccount\b",
        r"\bchange\b.*\bpayment\b",
    )

    SENSITIVE_OPERATIONS = { 
        "cancel_order", 
        }

    def __init__(
        self, 
        patterns: tuple[str, ...] | None = None,
        operations: set[str] | None = None,
    ) -> None:

        self.patterns = (
            patterns
            if patterns is not None
            else self.DEFAULT_PATTERNS
        )
        self.operations = (
            operations
            if operations is not None
            else self.SENSITIVE_OPERATIONS
        )


    def should_intervene(
        self, 
        request: ToolHumanReviewRequest
    ) -> bool:

        content = request.request
        operation = request.operation

        if operation in self.operations:
            return True

        return any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.patterns
        )
