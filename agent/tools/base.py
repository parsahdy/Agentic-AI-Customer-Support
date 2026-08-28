from abc import ABC, abstractmethod

from ..state import AgentState
from .schemas import (
    GetOrderInput,
    CancelOrderInput,
    CreateTicketInput,
    CustomerInfoInput,
    ToolResult,
)


class BaseTool(ABC):

    name: str
    description: str

    @abstractmethod
    def run(self, state: AgentState,
            arguments: dict) -> ToolResult:
        """
        Execute the tool using validated arguments.
        """
        pass


class SearchKBTool(BaseTool):

    name = "search_knowledge_base"
    description = "Search the knowledge base for relevant information."


    def __init__(self):
        self.kb = None


    def run(self, state: AgentState,
            arguments: dict) -> ToolResult:

        query = state["query"]

        if not query or not query.strip():
            return ToolResult(
                success=False,
                error="Query cannot be empty."
            )

        # Retrieval will be connected here later.
        return ToolResult(
            success=True,
            result={
                "query": query,
                "documents": []
            }
        )


class GetOrderTool(BaseTool):

    name = "get_order"
    description = "Get order information using an order ID."

    def run(self, state: AgentState,
            arguments: dict) -> ToolResult:

        try:
            validated = GetOrderInput(**arguments)
        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc)
            )

        # Mock data for now.
        order = {
            "order_id": validated.order_id,
            "status": "processing",
        }

        return ToolResult(
            success=True,
            result=order
        )


class CancelOrderTool(BaseTool):
    
    name = "cancel_order"
    description = "Cancel an existing order using its order ID."

    def run(self, state: AgentState,
            arguments: dict) -> ToolResult:

        try:
            validated = CancelOrderInput(**arguments)
        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc)
            )

        # Mock cancellation.
        return ToolResult(
            success=True,
            result={
                "order_id": validated.oredr_id,
                "status": "cancelled",
            }
        )


class CreateTicketTool(BaseTool):

    name = "create_ticket"
    description = "Create a customer support ticket."

    def run(self, state: AgentState,
            arguments: dict) -> ToolResult:

        try:
            validated = CreateTicketInput(**arguments)
        except Exception as exc:
            return ToolResult(
                success=True,
                error=str(exc)
            )

        ticket = {
            "subject": validated.subject.strip(),
            "message": validated.message.strip(),
            "priority": validated.priority.lower().strip(),
        }

        return ToolResult(
            success=True,
            result=ticket
        )


class CustomerInfoTool(BaseTool):

    name = "get_customer_info"
    description = "Get customer information using a customer ID."


    def run(self, state: AgentState,
            arguments: dict) -> ToolResult:

        try:
            validated = CustomerInfoInput(**arguments)
        except Exception as exc:
            return ToolResult(
                success=False,
                error=str(exc)
            )

        # Mock customer data.
        customer = {
            "customer_id": validated.customer_id,
            "name": "Mock Customer",
        }

        return ToolResult(
            success=True,
            result=customer
        )
