from knowledge_base import config

from .document_loader.transform_registry import TRANSFORMS
from .document_processor.processing_pipeline import build_pipeline
from .chunking.chunking_pipeline import chunk_pipeline
from .embedding.embedding_pipeline import embedding_pipeline
from .vector_store.vector_pipeline import vectorstore_pipeline
from .document_mapping.document_mapping import DocumentMapping

from knowledge_base.monitoring.monitor import KnowledgeBaseMonitor
from knowledge_base.monitoring.monitor_pipeline import monitor_pipeline

from knowledge_base.statistics.statistics_pipeline import statistics_pipeline

from knowledge_base.versioning.version_pipeline import versioning_pipeline



class KnowledgeBaseService:

    def __init__(self):
        self.config = config

    def build(self):

        monitor = KnowledgeBaseMonitor()

        # Document Transformation
        documents = monitor_pipeline(
            monitor=monitor,
            stage="document_tarnsformation",
            function=TRANSFORMS[self.config.CURRENT_TRANSFORM],
        )

        # Document Processing
        processed_pipeline = build_pipeline()
        processed_documents = monitor_pipeline(
            monitor=monitor,
            stage="document_processing",
            function=processed_pipeline.run,
            documents=documents,
        )

        # Chunking
        chunked_documents = monitor_pipeline(
            monitor=monitor,
            stage="chunking",
            function=chunk_pipeline,
            documents=processed_documents,
            chunker_type=self.config.CHUNKER_TYPE
        )

        # Embedding
        embeddings = monitor_pipeline(
            monitor=monitor,
            stage="embedding",
            function=embedding_pipeline,
            documents=chunked_documents,
            embedding_type=self.config.EMBEDDING_TYPE,
            model_name=self.config.SENTENCE_EMBEDDING_MODEL
        )

        # Vector store
        monitor_pipeline(
            monitor=monitor,
            stage="vector_store",
            function=vectorstore_pipeline,
            embeddings=embeddings,
            vector_type=self.config.VECTOR_STORE_TYPE
        )

        # Document mapping
        mapping = DocumentMapping()
        monitor_pipeline(
            monitor=monitor,
            stage="document_mapping",
            function=mapping.save_mapping,
            chunked_documents=chunked_documents,
        )

        statistics = statistics_pipeline(
            documents=documents,
            processed_documents=processed_documents,
            chunked_documents=chunked_documents,
            embeddings=embeddings
        )

        version_data = versioning_pipeline(
            version="v1",
            embedding_model=self.config.SENTENCE_EMBEDDING_MODEL,
            chunker_type=self.config.CHUNKER_TYPE,
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            vector_store_type=self.config.VECTOR_STORE_TYPE,
            document_count=len(documents),
            chunk_count=len(chunked_documents),
            embedding_dimension=embeddings.shape[1],
        )

        result = {
            "status": "success",
            "version": version_data,
            "statistics": statistics,
            "monitoring": monitor.records,
        }

        print("[INFO] Knowledge Base created successfully.")

        return result


def kb_pipeline() -> dict:

    kb = KnowledgeBaseService()
    return kb.build()



if __name__ == "__main__":
    result = kb_pipeline()

    print("\nKnowledgeBase version:")
    print(result["version"])

    print("\nKnowledge Base Statistics:")
    print(result["statistics"])

    print("\nPipeline Monitoring:")
    for record in result["monitoring"]:
        print(record)