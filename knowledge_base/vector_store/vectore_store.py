from abc import ABC, abstractmethod
from pathlib import Path

from ..config import K

import faiss
import numpy as np


class BaseVectorStore(ABC):

    @abstractmethod
    def build(self, embeddings: np.ndarray) -> None:
        """
        Build the vector index from embeddings.
        """
        pass



class FAISSVectorStore(BaseVectorStore):

    def __init__(self):
        self.index: faiss.Index | None = None

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


class QdrantVectorStore(BaseVectorStore):

    def build(self, embeddings: np.ndarray) -> None:
        raise NotImplementedError(
            "QdrantVectorStore is not implemented yet."
        )



class ChromaVectorStore(BaseVectorStore):

    def build(self, embeddings: np.ndarray) -> None:
        raise NotImplementedError(
            "ChromaVectorStore is not implemented yet."
        )
