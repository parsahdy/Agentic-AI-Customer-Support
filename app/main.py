from contextlib import asynccontextmanager

from fastapi import FastAPI

from agent import AgentService

from . import models
from .database import engine
from .routes.agent import router as agent_router


models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    ONE agent for the whole process: it owns the DB connections and the
    checkpointer that stores paused (waiting for human) conversations.
    """

    app.state.agent = AgentService()

    yield

    app.state.agent.close()


app = FastAPI(
    title="AI Customer Support API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(agent_router)