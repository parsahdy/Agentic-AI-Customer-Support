from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field



class QACreate(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


class QAOut(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)