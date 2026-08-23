from .chunking_tests import chunking
from knowledge_base.vector_store.document_mapping import DocumentMapping
from knowledge_base.vector_store.vector_repository import VectorStoreRepository
from knowledge_base.config import METADATA_PATH


def document_mapping():

    chunked_documents = chunking()
    mapping = DocumentMapping(repository=VectorStoreRepository(metadata_path=METADATA_PATH))
    mapping.save_mapping(chunked_documents=chunked_documents)

    print("Mapping metadata created successfully.")


if __name__ == "__main__":
    print(document_mapping())
