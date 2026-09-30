from langchain_core.tools import StructuredTool

from .schemas import (
    GetOrderInput,
    CancelOrderInput,
    CreateTicketInput,
    CustomerInfoInput,
)


def get_order(order_id: int) -> dict:
    """
    Get order information using an order ID.
    """

    order = {
        "order_id": order_id,
        "status": "processing",
    }

    return order


def cancel_order(order_id: int) -> dict:
    """
    Cancel an existing order using an order ID.
    """

    return {
        "order_id": order_id,
        "status": "cancelled",
    }


def create_ticket(
    subject: str,
    message: str,
    priority: str,
) -> dict:
    """
    Create a customer support ticket.
    """

    if not subject.strip():
        return {
            "error": "Ticket subject cannot be empty.",
        }

    if not message.strip():
        return {
            "error": "Ticket message cannot be empty.",
        }

    if not priority.strip():
        return {
            "error": "Ticket priority cannot be empty.",
        }

    ticket = {
        "subject": subject.strip(),
        "message": message.strip(),
        "priority": priority.lower().strip(),
    }

    return ticket


def get_customer_info(customer_id: str) -> dict:
    """
    Get customer information using a customer ID.
    """

    customer = {
        "customer_id": customer_id,
        "name": "Mock Customer",
    }

    return customer


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