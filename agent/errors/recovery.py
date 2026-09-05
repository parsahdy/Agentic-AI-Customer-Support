from __future__ import annotations

from typing import Any

from .classifier import ErrorClassifier, ErrorType


class RecoveryHandler:
    """ 
    Handles failures after retry decisions have been exhausted
    or when an error is not retryable.
    """

    @staticmethod
    def recover(error: Exception, *,
                tool_name: str, retry_count: int) -> dict[str, Any]:

        """
        Convert an internal tool failure
        into a structured recovery result.
        """

        error_type = ErrorClassifier.classify(error)

        if error_type == ErrorType.PERMANENT:
            message = (
                f"Tool '{tool_name}' failed because "
                "the request could not be processed."
            )

        elif error_type == ErrorType.TRANSIENT:
            message = (
                f"Tool '{tool_name}' is temporarily unavailable."
                "Please try agein later."
            )

        else:
            message = (
                f"Tool '{tool_name}' could not complete the request."
            )

        return {
            "sucesss": False,
            "tool_name": tool_name,
            "error_type": error_type.value,
            "error": str(error),
            "retry_count": retry_count,
            "recovered": True,
            "message": message,
        }