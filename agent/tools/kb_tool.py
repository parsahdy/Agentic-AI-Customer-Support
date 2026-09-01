from langchain_core.tools import StructuredTool
from knowledge_base.kb_service import KnowledgeBaseService

from .schemas import SearchKBInput, ToolResult


def search_knowledge_base(
    query: str,
    kb: KnowledgeBaseService,
) -> dict:
    """
    Search the knowledge base for relevant
    customer support information.
    """

    if not query.strip():
        return ToolResult(
            success=False,
            error="Query cannot be empty.",
        ).model_dump()

    try:
        documents = kb.search(query)

        return ToolResult(
            success=True,
            result={
                "query": query,
                "documents": documents,
            },
        ).model_dump()

    except Exception as exc:
        return ToolResult(
            success=False,
            error=str(exc),
        ).model_dump()


class SearchKBTool:

    @staticmethod
    def create(kb: KnowledgeBaseService) -> StructuredTool:

        def search(query: str) -> dict:
            return search_knowledge_base(
                query=query,
                kb=kb,
            )

        return StructuredTool.from_function(
            func=search,
            name="search_knowledge_base",
            description=(
                "Search the knowledge base for relevant "
                "customer support information."
            ),
            args_schema=SearchKBInput,
        )