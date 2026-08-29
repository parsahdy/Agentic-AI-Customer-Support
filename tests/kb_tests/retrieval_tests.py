from knowledge_base.retriever.retriever_pipeline import retriever_pipeline
from knowledge_base.vector_store.vector_repository import VectorStoreRepository
from knowledge_base.embedding.embedding_factory import EmbeddingFactory
from knowledge_base.config import INDEX_PATH, METADATA_PATH, SENTENCE_EMBEDDING_MODEL


def retriever():

    query = input("Ask question: ")
    query_embedding = EmbeddingFactory.create(
        embedding_type="sentence",
        model_name=SENTENCE_EMBEDDING_MODEL).embed_query(query)
    retreive_documents = retriever_pipeline(
        retriever_type="vector",
        query_embedding=query_embedding,
        index_path=INDEX_PATH,
        repository=VectorStoreRepository(index_path=INDEX_PATH,
                                         metadata_path=METADATA_PATH),
        k=5
    )

    return retreive_documents


if __name__ == "__main__":
    print(retriever())

