from pathlib import Path

import numpy as np

from .vector_factory import VectorStoreFactory
from .vector_repository import VectorStoreRepository
from knowledge_base import config


PROJECT_ROOT = config.PROJECT_ROOT
KB_DIR = config.KB_DIR
INDEX_PATH = config.INDEX_PATH


def vectorstore_pipeline(embeddings: np.ndarray,
                         vector_type: str = "faiss"):

    vector_store = VectorStoreFactory.create(vector_type)
    vector_store.build(embeddings)

    if vector_type == "faiss":

        repository = VectorStoreRepository(INDEX_PATH)
        repository.save_index(vector_store.index)

        print("Vector store created successfully.")


    return vector_store