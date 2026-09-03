from abc import ABC, abstractmethod

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver 



class ShortTermMemory(ABC):
    """
    Abstraction over thread-level persistence.

    LangGraph's checkpointer is responsible for persisting
    and restoring graph state for a conversation thread.
    """

    @abstractmethod
    def get_checkpointer(self) -> BaseCheckpointSaver:
        """
        Return the configured LangGraph checkpointer.
        """
        raise NotImplementedError


class InMemoryShortTermMemory(ShortTermMemory):
    """
    Development/test implementation.

    State exists only while this Python process is alive.
    """

    def __init__(self):
        self.checkpointer = InMemorySaver()


    def get_checkpointer(self) -> BaseCheckpointSaver:
        return self.checkpointer


class PostgresShortTermMemory(ShortTermMemory):

    def __init__(self, database_url: str):
        if not database_url:
            raise ValueError(
                "DATBASE_URL is required for Postgres memory."
            )

        self._checkpointer_context = PostgresSaver.from_conn_string(
            database_url
        )

        self.checkpointer = (
            self._checkpointer_context.__enter__()
        )

        self.checkpointer.setup()


    def get_checkpointer(self) -> BaseCheckpointSaver:

        if self._checkpointer_context is not None:
            self._checkpointer_context.__exit__(
                None,
                None,
                None,
            )

            self._checkpointer_context = None
            self.checkpointer = None

            