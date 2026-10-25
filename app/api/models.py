from datetime import datetime, UTC

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class QA(Base):
    __tablename__ = "qa"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        index=True
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False
    )


class PendingReview(Base):
    """
    A conversation that the agent paused because it needs a human decision.
 
    The paused graph itself lives in the LangGraph checkpointer. This table
    is the operator's to-do list (and, later, the audit history).
    """
 
    __tablename__ = "pending_reviews"
 
    review_id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )
 
    user_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
 
    session_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
 
    request: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
 
    # pending -> resolving (an operator took it) -> decided
    status: Mapped[str] = mapped_column(
        String,
        default="pending",
        nullable=False,
        index=True,
    )
 
    decision: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
 
    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
 
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
 
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )