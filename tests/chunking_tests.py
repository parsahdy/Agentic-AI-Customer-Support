from .document_processing_tests import document_processing
from knowledge_base.chunking.chunking_pipeline import chunk_pipeline




def chunking():

    documents = document_processing()
    chunked_documents = chunk_pipeline(documents=documents)

    return chunked_documents



if __name__ == "__main__":
    print(chunking())
