from fastapi import FastAPI

from api import models
from api.database import engine
from api.routes.question import router


models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Customer Support API",
    version="1.0.0",
)

app.include_router(router)