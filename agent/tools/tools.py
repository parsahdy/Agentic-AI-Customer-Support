from langchain_core.tools import StructuredTool

from .schemas import (
    GetOrderInput,
    CancelOrderInput,
    CreateTicketInput,
    CustomerInfoInput,
    ToolResult,
)


def get_order(order_id: int) -> dict:
    """
    Get order information using an order ID.
    """

    order = {
        "order_id": order_id,
        "status": "processing",
    }

    return ToolResult(
        success=True,
        result=order,
    ).model_dump()


def cancel_order(order_id: int) -> dict:
    """
    Cancel an existing order using an order ID.
    """

    return ToolResult(
        success=True,
        result={
            "order_id": order_id,
            "status": "cancelled",
        },
    ).model_dump()


def create_ticket(
    subject: str,
    message: str,
    priority: str,
) -> dict:
    """
    Create a customer support ticket.
    """

    if not subject.strip():
        return ToolResult(
            success=False,
            error="Ticket subject cannot be empty.",
        ).model_dump()

    if not message.strip():
        return ToolResult(
            success=False,
            error="Ticket message cannot be empty.",
        ).model_dump()

    if not priority.strip():
        return ToolResult(
            success=False,
            error="Ticket priority cannot be empty.",
        ).model_dump()

    ticket = {
        "subject": subject.strip(),
        "message": message.strip(),
        "priority": priority.lower().strip(),
    }

    return ToolResult(
        success=True,
        result=ticket,
    ).model_dump()


def get_customer_info(customer_id: str) -> dict:
    """
    Get customer information using a customer ID.
    """

    customer = {
        "customer_id": customer_id,
        "name": "Mock Customer",
    }

    return ToolResult(
        success=True,
        result=customer,
    ).model_dump()


get_order_tool = StructuredTool.from_function(
    func=get_order,
    name="get_order",
    description="Get order information using an order ID.",
    args_schema=GetOrderInput,
)

cancel_order_tool = StructuredTool.from_function(
    func=cancel_order,
    name="cancel_order",
    description="Cancel an existing order using an order ID.",
    args_schema=CancelOrderInput,
)

create_ticket_tool = StructuredTool.from_function(
    func=create_ticket,
    name="create_ticket",
    description="Create a customer support ticket.",
    args_schema=CreateTicketInput,
)

customer_info_tool = StructuredTool.from_function(
    func=get_customer_info,
    name="get_customer_info",
    description="Get customer information using a customer ID.",
    args_schema=CustomerInfoInput,
)