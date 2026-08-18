from langchain_text_splitters import RecursiveCharacterTextSplitter
from abc import ABC, abstractmethod

from ..config import CHUNKER


class ChunkerBase(ABC):

    @abstractmethod
    def chunk(documents: list[dict]) -> list[dict]:
        pass

class RecursiveCunker(ChunkerBase):

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNKER["chunk_size"],
            chunk_overlap=CHUNKER["chunk_overlap"],
            length_function=len,
            is_separator_regex=False
        )

    def chunk(self, documents: list[dict]) -> list[dict]:

        chunked_documents = []

        for document in documents:
            content = document.get("content", "")
            metadata = document.get("metadata", {}).copy()

            if not content:
                continue

            chunks = self.text_splitter.split_text(content)

            document_id = metadata.get("document_id", "unknown")

            for chunk_index, chunk in enumerate(chunks):

                chunk_metadata = metadata.copy()
                chunk_metadata["chunk_id"] = (
                    f"{document_id}_chunk_{chunk_index}"
                )
                chunk_metadata["chunk_index"] = chunk_index

                chunked_documents.append(
                    {
                        "content": chunk,
                        "metadata": chunk_metadata,
                    }
                )

        return chunked_documents
    
class SentenceChunker(ChunkerBase):

    def chunk(self, documents: list[dict]) -> list[dict]:
        """
        Placeholder for sentence-based chunking.
        """
        raise NotImplementedError(
            "SentenceChunker has not been implemented yet."
        )
