
class AgentError(Exception):
    """
    Base exception for agent-level errors.
    """


class TransientError(AgentError): 
    """
    Error that may succeed if the operation is retried.
    """


class PermanentError(AgentError): 
    """
    Error that should not be retried because 
    repeating the same operation is unlikely to fix the problem.
    """


# Agent-level errors
class TransientAgentError(TransientError):
    """
    Temporary fauilure during an agent operation.
    """


class PermanentAgentError(PermanentError):
    """
    Non-retryable failure during an agent operation.
    """


class LLMError(AgentError):
    """
    Base error for failures related to LLM interaction.
    """


class TransientLLMError(LLMError):
    """
    Temporary LLM failure that may succeed if retried.
    """


class PermanentLLMError(LLMError, PermanentError):
    """
    Non-retryable LLM failure.
    """


class KnowledgeBaseError(AgentError):
    """
    Base error for failures related to knowledge base operations.
    """


class TransientKnowledgeBaseError(KnowledgeBaseError,
                                  TransientError):
    """
    Temporary knowledge base failure that my succeed if retried.
    """


class PermanentKnowledgeBaseError(KnowledgeBaseError,
                                  PermanentError):
    """
    Non-retryable Knowledge base failure.
    """


class AgentMemoryError(AgentError):
    """
    Base error for failures related to agent memory operatons.
    """


class TransientMemoryError(AgentMemoryError, TransientError): 
    """
    Temporary memory failure that may succeed if retried.
    """ 


class PermanentMemoryError(AgentMemoryError, PermanentError): 
    """
    Non-retryable memory failure.
    """


class RouterError(PermanentAgentError):
    """
    Raised when the agent router cannot determine a valid route.
    """


class HumanReviewError(PermanentAgentError):
    """
    Raised when a human-review operation fails.
    """


class ConfidenceEvaluationError(PermanentAgentError):
    """
    Raised when confidence or evaluation logic fails.
    """


# Tool-Level errors
class TransientToolError(TransientError): 
    """ 
    Temporary failure during tool execution.
    """


class PermanentToolError(PermanentError): 
    """
    Non-retryable failure during tool execution. 
    """


class ToolNotFoundError(PermanentToolError):
    """ 
    Raised when the requested tool does not exist.
    """

    def __init__(self, tool_name: str):

        self.tool_name = tool_name

        super().__init__(
            f"Tool '{tool_name}' was not found."
        )


class ValidationError(PermanentToolError): 
    """ 
    Raised when tool input validation fails.
    """ 


class AuthenticationError(PermanentToolError): 
    """ 
    Raised when authentication fails.
    """ 


class AuthorizationError(PermanentToolError): 
    """ 
    Raised when authorization fails.
    """ 


class InvalidOrderIdError(PermanentToolError): 
    """ 
    Raised when an order ID is invalid.
    """