from .error_classifier import ErrorClassifier
from ..state import AgentState


class AgentErrorHandler:
    """
    Converts an agent exception into a structured error 
    that can be stored in AgentState.
    """

    def handle(
            self, 
            error: Exception,
            state: AgentState,
        ) -> dict:
        """
        Handle an exception and return a structured agent error.
        """

        classified_error = ErrorClassifier.classify(error)

        return {
            "type": classified_error["error_type"],
            "message": str(error),
            "node": state.get("current_node"),
            "retryable": classified_error["retryable"],
            "retry_count": 0,
        }