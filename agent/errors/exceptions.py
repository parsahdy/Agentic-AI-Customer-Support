
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
            f"Tool '{tool_name}' was notd found."
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