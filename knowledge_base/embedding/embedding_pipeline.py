from .embedding_factory import EmbeddingFactory
from ..config import SENTENCE_EMBEDDING_MODEL


def embedding_pipeline(documents: list[dict],
                       embedding_type: str = "sentence",
                       model_name: str = SENTENCE_EMBEDDING_MODEL):

    embedder = EmbeddingFactory.create(
        embedding_type=embedding_type,
        model_name=model_name
    )
    documents_embeddings = embedder.embed(documents)

    return documents_embeddings
