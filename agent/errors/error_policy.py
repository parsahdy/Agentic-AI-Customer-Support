from enum import Enum

from .agent_error_handler import AgentErrorHandler
from ..state import AgentState


class RecoveryAction(Enum):
	RETRY = "retry"
	HUMAN_REVIEW = "human_review"
	FAIL = "fail"


class ErrorPolicy:
	"""
    Determines the recovery action for an agent error.
    """
	
	def __init__(self) -> None:

		self.error_handler = AgentErrorHandler()

	def policy(
		self,
		error: Exception,
		state: AgentState,
	) -> RecoveryAction:
		"""
        Determine how the agent should recover from an exception.
        """

		error_info = self.error_handler.handle(error, state)

		retryable = error_info["retryable"]

		if retryable is True:
			return RecoveryAction.RETRY

		if retryable is False:
			return RecoveryAction.FAIL

		return RecoveryAction.HUMAN_REVIEW
		
