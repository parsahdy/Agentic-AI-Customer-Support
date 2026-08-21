from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
from langchain_community.retrievers import BM25Retriever as LangChainBM25Retriever

from .retrieval_config import K
from ..vector_store.vector_repository import VectorStoreRepository
from ..vector_store.document_mapping import DocumentMapping



class BaseRetriever(ABC):

    @abstractmethod
    def retrive(self, 
                query: str | None=None,
                query_embedding: np.ndarray | None=None,
                documents: list[dict] | None=None,
                k: int = K) -> list[dict]:
        """
        Retrive top-k relevent documents.
        """
        pass


class VectorRetriever(BaseRetriever):

    def __init__(self,
                 repository: VectorStoreRepository,
                 index_path: Path) -> list[dict]:
        
        self.repository = repository
        self.index_path = index_path
        self.mapping = DocumentMapping(repository)


    def retrive(self, 
                query: str | None=None,
                query_embedding: np.ndarray | None=None,
                documents: list[dict] | None=None,
                k: int = K) -> list[dict]:

        if query_embedding is None:
            raise ValueError(
                "query_embedding is required for VectorRetriever."
            )

        index = self.repository.load_index(self.index_path)
        scores, indices = index.search(query_embedding, k)

        return self.mapping.get_documents(
            indices=indices,
            scores=scores
        )


class BM25Retriever(BaseRetriever):

    def retrive(self, 
                query: str | None=None,
                query_embedding: np.ndarray | None=None,
                documents: list[dict] | None=None,
                k: int = K) -> list[dict]:

        if query is None:
            raise ValueError(
                "query is required for BM25Retriever."
            )

        if not documents:
            raise ValueError(
                "documents are required for BM25Retriever."
            )

        retriever = LangChainBM25Retriever.from_documents(
            documents,
            k=k
            )
        

        return retriever.invoke(query)


class HybridRetriever(BaseRetriever):

    def __init__(self,
                 vector_retriever: VectorRetriever):

        self.vector_retriever = vector_retriever
        self.bm25_retriever = BM25Retriever()

    def retrive(self, 
                query: str | None=None,
                query_embedding: np.ndarray | None=None,
                documents: list[dict] | None=None,
                k: int = K) -> list[dict]:

        if query is None:
            raise ValueError(
                "query is required for HybridRetriever."
            )

        if query_embedding is None:
            raise ValueError(
                "query_embedding is required for HybridRetriever."
            )

        if not documents:
            raise ValueError(
                "documents are required for HybridRetriever."
            )

        bm25_docs = self.bm25_retriever.retrive(
            query=query,
            documents=documents,
            k = k
            )
        vector_docs = self.vector_retriever.retrive(
            query_embedding=query_embedding,
            k=k
        )

        return self._merge_results(
            bm25_docs,
            vector_docs,
            k,
        )

    @staticmethod
    def _merge_results(
        bm25_docs: list[dict],
        vector_docs: list[dict],
        k: int = K):

        merged = []
        seen_ids = set()

        for document in bm25_docs + vector_docs:

            metadata = document.get("metadata", {})
            document_id = (
                metadata.get("chunk_id")
                or metadata.get("document_id")
            )

            if document_id in seen_ids:
                continue

            seen_ids.add(document_id)
            merged.append(document)

            if len(merged) >= k:
                break

        return merged