from .retriever import (
    BaseRetriever,
    VectorRetriever,
    BM25Retriever,
    HybridRetriever,
)

class RetrieverFactory:

    _retrievers: dict[str, type[BaseRetriever]] = {
        "vector": VectorRetriever,
        "bm25": BM25Retriever,
        "hybrid": HybridRetriever,
    }

    @classmethod
    def create(cls, retriever_type: str, **kwargs) -> BaseRetriever:

        retriever_type = retriever_type.lower().strip()

        if retriever_type not in cls._retrievers:
            raise ValueError(
                f"Retriever not found: {retriever_type}",
                f"Available retrievers: {list(cls._retrievers.keys())}"
            )

        retriever_class = cls._retrievers[retriever_type]

        if retriever_type == "vector":
            return retriever_class(
                repository=kwargs["repository"],
                index_path=kwargs["index_path"],
            )

        if retriever_type == "bm25":
            return retriever_class()

        if retriever_type == "hybrid":
            vector_retriever = vector_retriever(
                repository=kwargs["repository"],
                index_path=kwargs["index_path"],
            )

            return retriever_class(
                vector_retriever=vector_retriever
            )

        raise RuntimeError(
            f"Unable to create retriever: {retriever_type}"
        )