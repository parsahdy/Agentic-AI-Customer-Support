from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.store.base import BaseStore

from .short_term import (
    ShortTermMemory,
    InMemoryShortTermMemory,
    PostgresShortTermMemory,
)

from .long_term import (
    LongTermMemory,
    InMemoryLongTermMemory,
    PostgresLongTermMemory,
)

from .config import MEMORY_BACKEND, DATABASE_URL



class MemoryService:

    def __init__(
        self,
        short_term: ShortTermMemory | None=None,
        long_term: LongTermMemory | None=None,
    ):

        self.short_term = (
            short_term
            if short_term is not None
            else self._create_short_term()
        )

        self.long_term = (
            long_term
            if long_term is not None
            else self._create_long_term()
        )


    def _create_short_term(self) -> ShortTermMemory:

        if MEMORY_BACKEND == "postgres":
            return PostgresShortTermMemory(
                DATABASE_URL
            )

        return InMemoryShortTermMemory()


    def _create_long_term(self) -> LongTermMemory:

        if MEMORY_BACKEND == "postgres":
            return PostgresLongTermMemory(
                DATABASE_URL
            )

        return InMemoryLongTermMemory()


    def get_checkpointer(self) -> BaseCheckpointSaver:
        return self.short_term.get_checkpointer()


    def get_store(self) -> BaseStore:
        return self.long_term.get_store()


    def save_memory(self, user_id: str,
                    key: str, value: dict[str, Any],
                    ) -> None:

        namespace = ("users", user_id)

        self.get_store().put(
            namespace,
            key,
            value,
        )


    def get_memory(self, user_id: str,
                   key: str):

        namespace = ("users", user_id)

        return self.get_store().get(
            namespace,
            key,
        )


    def search_memories(self, user_id: str,
                        query: str, limit: int = 5):

        namespace = ("users", user_id)

        return self.get_store().search(
            namespace,
            query=query,
            limit=limit,
        )
        