from .embedding_tests import embedding
from knowledge_base.vector_store.vector_pipeline import vectorstore_pipeline



def vector_store():

    embeddings = embedding()
    vector_store = vectorstore_pipeline(embeddings=embeddings)

    return vector_store



if __name__ == "__main__":
    print(vector_store())