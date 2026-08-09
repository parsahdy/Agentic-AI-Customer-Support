from abc import ABC, abstractmethod
from typing import Any

import unicodedata
import re


Document = dict[str, Any]

class BaseProcessor(ABC):

    @abstractmethod
    def process(self, documents: list[Document]) -> list[Document]:
        """
        Process a list of documents and return the processed documents.
        """
        pass

class TextProcessor(BaseProcessor):

    def process(self, documents: list[Document]) -> list[Document]:

        processed_documents = []

        for document in documents:

            content = document.get("content")

            if not content:
                continue

            content = str(content)

            content = unicodedata.normalize("NFKC", content)
            content = content.replace("\r\n", "\n")
            content = content.replace("\r", "\n")
            content = re.sub(r"[^\w\s?!]", "", content)
            content = re.sub(r"\s+", " ", content).strip()
            content = "".join(char for char in content
                        if char.isprintable() or char in "\n\t")
            content = content.lower()

            processed_document = document.copy()
            processed_document["content"] = content
            processed_documents.append(processed_document)

        return processed_documents

class MetaDataProcessor(BaseProcessor):

    def process(self, documnets: list[Document]) -> list[Document]:

        valid_documents = []

        for document in documnets:

            metadata = document.get("metadata")

            if not isinstance(metadata, dict):
                continue

            if not document.get("content"):
                continue

            valid_documents.append(document)

        return valid_documents

class DuplicationProcessor(BaseProcessor):

    def process(self, documents: list[Document]) -> list[Document]:

        unique_documents = []
        seen = set()

        for document in documents:
            content = document.get("content", "").strip()

            if not content:
                continue

            if content in seen:
                continue

            seen.add(content)
            unique_documents.append(document)

        return unique_documents