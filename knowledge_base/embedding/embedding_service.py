from abc import ABC, abstractmethod

import numpy as np
from sentence_transformers import SentenceTransformer
from FlagEmbedding import BGEM3FlagModel


class BaseEmbedding(ABC):

    @abstractmethod
    def embed(self, documents: list[dict]) -> np.ndarray:
        """
        Generate embeddings for documents.
        """
        pass


    @abstractmethod
    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a user query.
        """
        pass



class SentenceTransformerEmbedding(BaseEmbedding):

    def __init__(self, model_name: str):
        self.model_name = model_name

        print(
            f"[INFO] Loading SentenceTransformer model: "
            f"{self.model_name}"
        )

        self.model = SentenceTransformer(self.model_name)


    def embed(self, documents: list[dict]) -> np.ndarray:

        texts = [
            document["content"]
            for document in documents
            if document.get("content")
        ]

        if not texts:
            return np.empty((0, 0), dtype=np.float32)

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.astype(np.float32)


    def embed_query(self, query: str) -> np.ndarray:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding.astype(np.float32)


class BGEEmbedding(BaseEmbedding):

    def __init__(self, model_name: str):
        self.model_name = model_name

        print(
            f"[INFO] Loading BGE model: "
            f"{self.model_name}"
        )

        self.model = BGEM3FlagModel(self.model_name, use_fp16=True)

    
    def embed(self, documents: list[dict]) -> np.ndarray:

        texts = [
            document["content"]
            for document in documents
            if document.get("content")
        ]

        if not texts:
            return np.empty((0, 0), dtype=np.float32)

        result = self.model.encode(
            texts,
            batch_size=12,
            max_length=8192,
        )

        embeddings = result["dense_vecs"]

        return np.asarray(
            embeddings,
            dtype=np.float32,
        )


    def embed_query(self, query: str) -> np.ndarray:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        result = self.model.encode(
            [query],
            batch_size=1,
            max_length=8192,
        )

        embedding = result["dense_vec"][0]

        return np.asarray(
            embedding,
            dtype=np.float32,
        )