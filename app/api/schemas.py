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


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    user_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)


class AskResponse(BaseModel):
    status: str                      # success | human_review | fail
    final_answer: str = ""
    route: str | None = None
    review_id: str | None = None     # set only when status == "human_review"
    error: dict | None = None


class PendingReview(BaseModel):
    review_id: str
    user_id: str
    session_id: str
    request: dict
 
    model_config = ConfigDict(from_attributes=True)