from langchain_core.tools import StructuredTool

from .tools import (
    get_order_tool,
    cancel_order_tool,
    create_ticket_tool,
    customer_info_tool,
)

from .kb_tool import SearchKBTool

from knowledge_base.kb_service import KnowledgeBaseService



class ToolRegistry:

    def __init__(self, kb: KnowledgeBaseService | None=None) -> None: 

        self.kb = kb

        self._tools: dict[str, StructuredTool] = {
            get_order_tool.name: get_order_tool,
            cancel_order_tool.name: cancel_order_tool,
            create_ticket_tool.name: create_ticket_tool,
            customer_info_tool.name: customer_info_tool,
        }

        if kb is not None:
            self._tools["search_knowledge_base"] = (
                SearchKBTool.create(kb)
            )


    def register(self, tool: StructuredTool) -> None:

        if not isinstance(tool, StructuredTool):
            raise TypeError(
                "Registered tool must be a StructuredTool."
            )

        if tool.name in self._tools:
            raise ValueError(
                f"Tool Already registered: {tool.name}"
            )

        self._tools[tool.name] = tool


    def get(self, name: str) -> type[StructuredTool]:

        if name not in self._tools:
            raise ValueError(
                f"Tool not found: {name}. "
                f"Available tools: {list(self._tools.keys())}"
            )

        return self._tools[name]


    def list_tools(self) -> list[str]:

        return list(self._tools.keys())


    def get_tools(self) -> list[StructuredTool]:

        return list(self._tools.values())


    def get_tool(self, name: str) -> StructuredTool:

        return self.get(name)


    