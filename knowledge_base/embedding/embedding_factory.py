from .embedding_service import (
    BaseEmbedding, 
    SentenceTransformerEmbedding,
    BGEEmbedding,
)



class EmbeddingFactory:

    _embedding_models: dict[str, type[BaseEmbedding]] = {
        "sentence": SentenceTransformerEmbedding,
        "bge": BGEEmbedding,
    }

    @classmethod
    def create(cls, embedding_type: str, model_name: str) -> BaseEmbedding:

        embedding_type = embedding_type.lower().strip()

        if not embedding_type in cls._embedding_models:
            raise ValueError(
                f"Embedding model not found: {embedding_type}"
                f"Available Embedding models: {list(cls._embedding_models.keys())}"
            )

        embedding_class = cls._embedding_models[embedding_type]
        return embedding_class(model_name)