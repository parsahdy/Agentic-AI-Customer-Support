from .base import (
    BaseTool,
    SearchKBTool,
    GetOrderTool,
    CancelOrderTool,
    CreateTicketTool,
    CustomerInfoTool,
)


class ToolRegistry:

    def __init__(self):

        self._tools: dict[str, type[BaseTool]] = {
            SearchKBTool.name: SearchKBTool,
            GetOrderTool.name: GetOrderTool,
            CancelOrderTool.name: CancelOrderTool,
            CreateTicketTool.name: CreateTicketTool,
            CustomerInfoTool.name: CustomerInfoTool,
        }

    def register(self, tool: type[BaseTool]) -> None:

        if not issubclass(tool, BaseTool):
            raise ValueError(
                "Registered tool must inherit from BaseTool."
            )

        if tool.name in self._tools:
            raise ValueError(
                f"Tool Already registered: {tool.name}"
            )

        self._tools[tool.name] = tool


    def get(self, name: str) -> type[BaseTool]:

        if name not in self._tools:
            raise ValueError(
                f"Tool not found: {name}. "
                f"Available tools: {list(self._tools.keys())}"
            )

        return self._tools[name]


    def create(self, name: str) -> BaseTool:

        tool_class = self.get(name)

        return tool_class()


    def list_tools(self) -> list[str]:

        return list(self._tools.keys())


    def get_tools(self) -> list[BaseTool]:
        return [
            tool_class()
            for tool_class in self._tools.values()
        ]


    