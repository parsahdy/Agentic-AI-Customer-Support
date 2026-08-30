from .embedding_factory import EmbeddingFactory
from .embedding_service import BaseEmbedding



class EmbeddingPipeline:

    def __init__(self, embedding_type: str,
                 model_name: str) -> None:

        self.embedder: BaseEmbedding = EmbeddingFactory.create(
            embedding_type=embedding_type,
            model_name=model_name
        )
        

    def documents_embedding(self, documents: list[dict],
                            embedding_type: str):

        documents_embeddings = self.embedder.embed(documents)

        return documents_embeddings



    def query_embedding(self, query: str):

        query_embedding = self.embedder.embed_query(query)

        return query_embedding


def build_embedding_pipeline(
        embedding_type: str,
        model_name: str) -> EmbeddingPipeline:

    return EmbeddingPipeline(
        embedding_type=embedding_type,
        model_name=model_name
    )