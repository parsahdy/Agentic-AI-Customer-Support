from knowledge_base import config

from .document_loader import document_transform
from .document_processor.processing_pipeline import build_pipeline
from .chunking.chunking_pipeline import chunk_pipeline
from .embedding.embedding_pipeline import embedding_pipeline
from .vector_store.vector_pipeline import vectorstore_pipeline
from .document_mapping.document_mapping import DocumentMapping




class KnowledgeBaseService:

    def __init__(self):
        self.config = config

    def build(self):

        # Document Transformation
        documents = document_transform.faq_transform()

        # Document Processing
        processed_pipeline = build_pipeline()
        processed_documents = processed_pipeline.run(documents)

        # Chunking
        chunked_documents = chunk_pipeline(
            documents=processed_documents,
            chunker_type=self.config.CHUNKER_TYPE
        )

        # Embedding
        embeddings = embedding_pipeline(
            documents=chunked_documents,
            embedding_type=self.config.EMBEDDING_TYPE,
            model_name=self.config.SENTENCE_EMBEDDING_MODEL
        )

        # Vector store
        vectorstore_pipeline(
            embeddings=embeddings,
            vector_type=self.config.VECTOR_STORE_TYPE
        )

        # Document mapping
        mapping = DocumentMapping()
        mapping.save_mapping(chunked_documents)

        print("[INFO] Knowledge Base created successfully.")


def kb_pipeline() -> None:

    kb = KnowledgeBaseService()
    kb.build()



if __name__ == "__main__":
    kb_pipeline()