from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, Request, status
from api.schemas import AskRequest, AskResponse, PendingReview
from sqlalchemy import update
from sqlalchemy.orm import Session

from agent import AgentService
from agent.human_loop.models import HumanDecision

from api import database
from api.models import PendingReview as PendingReviewRow


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


# Pending reviews live in the `pending_reviews` table (see models.py).
#
# The paused graph itself is stored by the LangGraph checkpointer. The table
# only answers "who is waiting for an operator?", and keeps the history of
# decisions. Both survive a server restart.

def _review_id(user_id: str, session_id: str) -> str:
    return f"{user_id}:{session_id}"
 
 
def _get_agent(request: Request) -> AgentService:
    agent = getattr(request.app.state, "agent", None)
 
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent is not initialised.",
        )
 
    return agent


def _to_response(
    output: dict,
    user_id: str,
    session_id: str,
    db: Session,
) -> AskResponse:
    """Convert the agent output into an API response."""

    review_id = None

    # A real interrupt: waiting for a human (no error, a request exists).
    waiting_for_human = (
        output.get("status") == "human_review"
        and output.get("error") is None
        and output.get("human_review_required") is not None
        and output.get("human_decision") is None
    )

    if waiting_for_human:
        review_id = _review_id(user_id, session_id)

        # merge = insert, or overwrite when the same session is paused again
        db.merge(
            PendingReviewRow(
                review_id=review_id,
                user_id=user_id,
                session_id=session_id,
                request=output["human_review_request"],
                status="pending",
                decision=None,
                comment=None,
                decided_at=None,
            )
        )
        db.commit()

    return AskResponse(
        status=output.get("status","fail"),
        final_answer=output.get("final_answer", ""),
        route=output.get("route"),
        review_id=review_id,
        error=output.get("error"),
    )


@router.post("/ask", response_model=AskResponse)
def ask(
    body: AskResponse,
    request: Request,
    db: Session = Depends(database.get_db),
):
    """Send a user query to the agent."""

    agent = _get_agent(request)

    try:
        output = agent.run(
            query=body.query,
            user_id=body.user_id,
            session_id=body.session_id,
        )
    except ValueError as exc:        # guardrail / validation errors    
        raise HTTPException(status_code=400, detail=str(exc))

    return _to_response(output, body.user_id, body.session_id)


@router.get("/reviews/pending", response_model=list[PendingReview])
def pending_reviews(db: Session = Depends(database.get_db)):
    """List request that are waiting for a human decison."""

    return (
        db.query(PendingReviewRow)
        .filter(PendingReviewRow.status == "pending")
        .order_by(PendingReviewRow.created_at)
        .all()
    )


@router.post("/reviews/{review_id}/decision", response_model=AskResponse)
def decide(
    review_id: str,
    decision: HumanDecision,
    request: Request,
    db: Session = Depends(database.get_db),
):
    """
    Give the human decision (approve / reject / escalate) for a paused
    request. The agent resumes from exactly where it stopped.
    """

    agent = _get_agent(request)

    # Take the review atomically: only ONE operator can move it from
    # "pending" to "resolving". A second operator gets 409.
    claimed = db.execute(
        update(PendingReviewRow)
        .where(
            PendingReviewRow.review_id == review_id,
            PendingReviewRow.status == "pending",
        )
        .values(status="resolving")
    ).rowcount
    db.commit()

    if claimed == 0:
        exists = db.get(PendingReviewRow, review_id) is not None

        raise HTTPException(
            status_code=409 if exists else 404,
            detail=(
                "This review was already taken or decided."
                if exists
                else "No review with this id."
            ),
        )

    review = db.get(PendingReviewRow, review_id)

    try:
        output = agent.resume(
            decision=decision.model_dump(),
            user_id=review.user_id,
            session_id=review.session_id,
        )
    except Exception:
        # The agent could not continue: give the review back.
        review.status = "pending"
        db.commit()
        raise

    review.status = "decide"
    review.decision = decision.decision
    review.comment = decision.comment
    review.decided_at = decision.now(UTC)
    db.commit()

    return _to_response(output, review.user_id, review.session_id)