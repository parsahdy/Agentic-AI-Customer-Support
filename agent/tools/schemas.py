from pydantic import BaseModel, Field


class GetOrderInput(BaseModel):
    order_id: int = Field(
        ...,
        description="The ID of the order."
    )


class CancelOrderInput(BaseModel):
    oredr_id: int = Field(
        ...,
        description="The ID of the order to cancel."
    )


class CreateTicketInput(BaseModel):
    subject: str = Field(
        ...,
        description="Short subject of the support ticket."
    )

    message: str = Field(
        ...,
        description="Detailed description of the customer's issue."
    )

    priority: str = Field(
        ...,
        description="Ticket priority such as low, medium, or high."
    )


class CustomerInfoInput(BaseModel):
    customer_id: str = Field(
        ...,
        description="The ID of the customer."
    )


class ToolResult(BaseModel):
    success: bool
    result: dict | None = None
    error: str | None = None
