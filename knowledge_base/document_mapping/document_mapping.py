from pathlib import Path
import numpy as np

from ..vector_store.vector_repository import VectorStoreRepository
from knowledge_base import config


class DocumentMapping:

    def __init__(self):
        self.repository = VectorStoreRepository(metadata_path=config.METADATA_PATH)


    def build_mapping(self, chunked_documents: list[dict]) -> list[dict]:

        mapping = []

        for vector_id, document in enumerate(chunked_documents):

            metadata = document.get("metadata", {})

            mapping.append(
                {
                    "vector_id": vector_id,
                    "document_id": metadata.get("document_id"),
                    "chunk_id": metadata.get("chunk_id"),
                    "metadata": metadata,
                }
            )

        return mapping

    
    def save_mapping(self, chunked_documents: list[dict]) -> None:

        mapping = self.build_mapping(chunked_documents)
        self.repository.save_metadata(mapping)


    def get_documents(self, 
                      indices: np.ndarray,
                      scores: np.ndarray) -> list[dict]:

        mapping = self.repository.load_metadata()

        results = []

        for vector_id, score in zip(indices[0], scores[0]):

            vector_id = int(vector_id)

            if vector_id == -1:
                continue

            document = mapping[vector_id]

            results.append(
                {
                    "vector_id": vector_id,
                    "document_id": document["document_id"],
                    "chunk_id": document["chunk_id"],
                    "metadata": document["metadata"],
                    "score": round(float(score), 2), 
                }
            )

        return results
