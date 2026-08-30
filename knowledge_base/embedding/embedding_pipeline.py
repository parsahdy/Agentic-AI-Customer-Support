from .embedding_factory import EmbeddingFactory


def embedding_pipeline(documents: list[dict],
                       embedding_type: str,
                       model_name: str):

    embedder = EmbeddingFactory.create(
        embedding_type=embedding_type,
        model_name=model_name
    )
    documents_embeddings = embedder.embed(documents)

    return documents_embeddings



def query_embedding(query: str,
                    embedding_type: str,
                    model_name: str):

    embedder = EmbeddingFactory.create(
        embedding_type=embedding_type,
        model_name=model_name
    )

    query_embedding = embedder.embed_query(query)

    return query_embedding