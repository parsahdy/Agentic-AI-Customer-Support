from langchain_core.tools import StructuredTool

from ..state import AgentState
from .registry import ToolRegistry
from .schemas import ToolResult


class ToolExecutor:

    def __init__(self, registry: ToolRegistry):

        self.registry = registry


    def execute(self, tool_name: str,
                state: AgentState,
                arguments: dict) -> ToolResult:

        try:

            tool: StructuredTool = self.registry.get(tool_name)

            result = tool.invoke(arguments)

            return ToolResult(
                success=True,
                result=result,
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc)
            )

        