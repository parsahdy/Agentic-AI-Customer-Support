from .statistics import KnowledgeBaseStatistics


def statistics_pipeline(
        documents,
        processed_documents,
        chunked_documents,
        embeddings,
):

    statistics = KnowledgeBaseStatistics()

    documents_stats = statistics.document_stats(
        documents,
        processed_documents
    )

    chunked_documents = statistics.chunk_stats(
        chunked_documents
    )

    embedding_stats = statistics.embedding_stats(
        embeddings
    )

    return {
        **documents_stats,
        **chunked_documents,
        **embedding_stats
    }
    