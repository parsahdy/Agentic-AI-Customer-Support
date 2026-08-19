from .vectore_store import (
    BaseVectorStore,
    FAISSVectorStore,
    QdrantVectorStore,
    ChromaVectorStore,
)


class VectorStoreFactory:

    _vector_stores: dict[str, type[BaseVectorStore]] = {
        "faiss": FAISSVectorStore,
        "qdrant": QdrantVectorStore,
        "chroma": ChromaVectorStore,
    }

    @classmethod
    def create(cls, vector_type: str) -> BaseVectorStore:

        vector_type = vector_type.lower().strip()

        if vector_type not in cls._vector_stores:
            raise ValueError(
                f"Vector store type not found: {vector_type}."
                f"Available vector stores: {list(cls._vector_stores.keys())}"
            )

        vector_store_class = cls._vector_stores[vector_type]
        return vector_store_class()