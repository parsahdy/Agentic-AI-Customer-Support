from pathlib import Path

import numpy as np

from .retriever_factory import RetrieverFactory
from ..config import K
from ..vector_store.vector_repository import VectorStoreRepository


def retriever_pipeline(retriever_type: str,
                       query: str | None=None,
                       query_embedding: np.ndarray | None=None,
                       documents: list[dict] | None=None,
                       repository: VectorStoreRepository | None=None,
                       k: int = K) -> list[dict]:

    if repository is None:
        raise ValueError(
            "VectorStoreRepository is required."
        )

    retriever = RetrieverFactory.create(
        retriever_type=retriever_type,
        repository=repository,
        )

    return retriever.retrive(
        query=query,
        query_embedding=query_embedding,
        documents=documents,
        k=k
    )

