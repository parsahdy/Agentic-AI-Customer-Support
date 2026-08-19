from pathlib import Path

import numpy as np

from .vector_factory import VectorStoreFactory
from .vector_repository import VectorStoreRepository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
KB_DIR = PROJECT_ROOT / "data" / "knowledge_base" 
INDEX_PATH = KB_DIR / "vector_index.faiss"


def vectorstore_pipeline(embeddings: np.ndarray,
                         vector_type: str = "faiss"):

    vector_store = VectorStoreFactory.create(vector_type)
    vector_store.build(embeddings)

    if vector_type == "faiss":

        repository = VectorStoreRepository(INDEX_PATH)
        repository.save_index(vector_store.index)


    return vector_store