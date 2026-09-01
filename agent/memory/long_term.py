from abc import ABC, abstractmethod

from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore
from langgraph.store.postgres import PostgresStore



class LongTermMemory(ABC):

    @abstractmethod
    def get_store(self) -> BaseStore:
        raise NotImplementedError


class InMemoryLongTermMemory(LongTermMemory):
    """
    Development/test implementation of long-term memory.
    """

    def __init__(self):
        self.store = InMemoryStore()


    def get_store(self) -> BaseStore:
        return self.store


class PostgresLongTermMemory(LongTermMemory):

    def __init__(self, database_url: str):
        if not database_url:
            raise ValueError(
                "DATABASE_URL is required for Postgres memory."
            )

        self.store = PostgresStore.from_conn_string(
            database_url
        )

        self.store.setup()


    def get_store(self) -> BaseStore:
        return self.store 