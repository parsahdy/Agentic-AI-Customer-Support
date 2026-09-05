from __future__ import annotations 
import time

from langchain_core.tools import StructuredTool

from ..state import AgentState
from ..errors import ErrorClassifier, RetryPolicy
from .registry import ToolRegistry
from .schemas import ToolResult



class ToolExecutor:

    def __init__(self, registry: ToolRegistry,
                 retry_policy: RetryPolicy | None = None):

        self.registry = registry
        self.retry_policy = retry_policy or RetryPolicy()


    def execute(self, tool_name: str,
                arguments: dict) -> ToolResult:

        retry_count = 0

        while True:
            try:

                tool: StructuredTool = self.registry.get_tool(tool_name)

                result = tool.invoke(arguments)

                return ToolResult(
                    success=True,
                    result=result,
                    retry_count=retry_count,
                )

            except Exception as exc:

                if self.retry_policy.should_retry(exc, retry_count):
                    retry_count += 1

                    delay = self.retry_policy.get_delay(retry_count)

                    time.sleep(delay)

                    continue

                error_type = ErrorClassifier.classify(exc)

                return ToolResult(
                    success=False,
                    error=str(exc),
                    error_type=error_type.value,
                    retry_count=retry_count,
                )

        