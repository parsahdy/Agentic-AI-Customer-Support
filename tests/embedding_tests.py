from .chunking_tests import chunking
from knowledge_base.embedding.embedding_pipeline import embedding_pipeline


def embedding():

    documents = chunking()
    embedding_documents = embedding_pipeline(documents=documents)

    return embedding_documents
    



if __name__ == "__main__":
    print(embedding())