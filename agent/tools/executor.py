from ..state import AgentState
from .registry import ToolRegistry
from .schemas import ToolResult



class ToolExecutor:

    def __init__(self, registry: ToolRegistry):

        self. registry = registry


    def execute(self, tool_name: str,
                state: AgentState,
                arguments: dict) -> ToolResult:

        try:

            tool = self.registry.create(tool_name)

            result = tool.run(
                state=state,
                arguments=arguments
            )

            return result

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc)
            )

        