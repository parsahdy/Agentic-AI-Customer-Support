from abc import ABC, abstractmethod
from pathlib import Path

import faiss
import numpy as np


class BaseVectorStore(ABC):

    @abstractmethod
    def build(self, embeddings: np.ndarray):
        """
        Build the vector index from embeddings.
        """
        pass

    @abstractmethod
    def search(self, query_embedding: np.ndarray,
               k: int = 5) -> tuple[np.ndarray, np.ndarray]:
        """
        Search the vector store and return scores and indices.
        """
        pass


class FAISSVectorStore(BaseVectorStore):

    def __init__(self):
        self.index = faiss.Index | None = None

    def build(self, embeddings: np.ndarray) -> None:

        if embeddings.size == 0:
            raise ValueError("Embeddings cannot be empty.")
        
        if embeddings.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2-dimensional numpy array."
            )

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings.astype(np.float32))


    def search(self, query_embedding: np.ndarray,
               k: int = 5) -> tuple[np.ndarray, np.ndarray]:

        if self.index is None:
            raise RuntimeError(
                "vector store has not been built or loaded."
            )

        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        query_embedding = query_embedding.astype(np.float32)

        scores, indices = self.index.search(
            query_embedding,
            k,
        )

        return scores, indices


class QdrantVectorStore(BaseVectorStore):

    def build(self, embeddings: np.ndarray) -> None:
        raise NotImplementedError(
            "QdrantVectorStore is not implemented yet."
        )

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5):

        raise NotImplementedError(
            "QdrantVectorStore is not implemented yet."
        )


class ChromaVectorStore(BaseVectorStore):

    def build(self, embeddings: np.ndarray) -> None:
        raise NotImplementedError(
            "ChromaVectorStore is not implemented yet."
        )

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5):
        
        raise NotImplementedError(
            "ChromaVectorStore is not implemented yet."
        )