from knowledge_base.kb_service import KnowledgeBaseService

from .base import BaseTool
from ..state import AgentState
from .schemas import SearchKBInput, ToolResult



class SearchKBTool(BaseTool):

    name = "search_knowledge_base"
    description = (
        "Search the knowledge base for relevant "
        "customer support information."
    )
    args_schema = SearchKBInput


    def __init__(self, kb: KnowledgeBaseService) -> None:
        self.kb = kb


    def run(self, state: AgentState,
            arguments: dict) -> ToolResult:

        try:

            validated = self.args_schema(**arguments)

            documents = self.kb.search(validated.query)
        
            return ToolResult(
                success=True,
                result={
                    "query": validated.query,
                    "documents": documents,
                }
            )

        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc)
            )