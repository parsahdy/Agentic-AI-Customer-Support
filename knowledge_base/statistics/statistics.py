from abc import ABC, abstractmethod

import numpy as np


class BaseStatistics(ABC):

    @abstractmethod
    def document_stats(self, documents: list[dict],
                       processed_documents: list[dict]) -> dict:
        """Calculate statistics related to documents."""
        pass

    @abstractmethod
    def chunk_stats(self, chunked_documents: list[dict]) -> dict:
        """Calculate statistics related to chunks."""
        pass

    @abstractmethod
    def embedding_stats(self, embeddings: np.ndarray) -> dict:
        """Calculate statistics related to embeddings."""
        pass



class KnowledgeBaseStatistics(BaseStatistics):

    def document_stats(self, documents: list[dict],
                       processed_documents: list[dict]) -> dict:

        return {
            "input_documents": len(documents),
            "processed_documents": len(processed_documents),
            "removed_documents": (
                len(documents) - len(processed_documents)
            ),
        }

    def chunk_stats(self, chunked_documents: list[dict]) -> dict:

        if not chunked_documents:
            return {
                "chunk_count": 0,
                "average_chunk_length": 0,
                "min_chunk_length": 0,
                "max_chunk_length": 0,
            }

        chunk_lenghts = [
            len(document.get("content", ""))
            for document in chunked_documents
        ]

        return {
            "chunk_count": len(chunked_documents),
            "average_chunk_length": round((sum(chunk_lenghts) / len(chunk_lenghts)), 2),
            "min_chunk_length": min(chunk_lenghts),
            "max_chunk_length": max(chunk_lenghts),

        }

    def embedding_stats(self, embeddings: np.ndarray) -> dict:

        if embeddings.size == 0:
            return {
                "embedding_count": 0,
                "embedding_dimension": 0,
            }

        if embeddings.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2-dimensional numpy array."
            )

        return {
            "embedding_count": embeddings.shape[0],
            "embedding_dimension": embeddings.shape[1]
        }

    