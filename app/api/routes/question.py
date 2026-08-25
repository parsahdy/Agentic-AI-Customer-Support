from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import database, models, schemas


router = APIRouter(
    prefix="/qa",
    tags=["qa"],
)


@router.post(
    "/ask",
    response_model=schemas.QAOut,
    status_code=status.HTTP_201_CREATED,
)
def ask_question(
    request: schemas.QACreate,
    db: Session = Depends(database.get_db),
):

    answer = ask(request.question)

    qa = models.QA(
        question=request.question,
        answer=answer,
    )

    db.add(qa)
    db.commit()
    db.refresh(qa)

    return qa


@router.get(
    "/",
    response_model=list[schemas.QAOut],
    status_code=status.HTTP_200_OK,
)
def show_qa(
    db: Session = Depends(database.get_db),
):
    return db.query(models.QA).all()