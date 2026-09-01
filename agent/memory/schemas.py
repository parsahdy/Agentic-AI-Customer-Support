from datetime import datetime, UTC

from pydantic import BaseModel, Field



class MemoryRecord(BaseModel):
    """
    A persistent piece of information associated with a user.
    """

    key: str = Field(
        min_length=1,
        description="Unique key identifying the memory."
    )

    value: dict = Field(
        default=dict,
        description="Structured memory payload."
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )