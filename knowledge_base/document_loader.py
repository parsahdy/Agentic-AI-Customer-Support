"""
The Document Loader only needs to read the data source
and convert it into a standard Document format.
"""

from abc import ABC, abstractmethod
from PyPDF2 import PdfReader
from pathlib import Path

import pandas as pd


class BaseDocumentLoader(ABC):

    @abstractmethod
    def load(self, source: str | Path) -> list:
        """
        load documents from the given source.
        """
        pass


class CSVDocumentLoader(BaseDocumentLoader):

    def load(self, source: str | Path) -> list:
        df = pd.read_csv(source)
        return df.to_dict(orient='records')


class ExcelDocumentLoader(BaseDocumentLoader):

    def load(self, source: str | Path) -> list:
        df = pd.read_excel(source)
        return df.to_dict(orient='records')


class JSONDocumentLoader(BaseDocumentLoader):

    def load(self, source: str | Path) -> list:
        df = pd.read_json(source)
        return df.to_dict(orient='records')


class PDFDocumentLoader(BaseDocumentLoader):

    def load(self, source: str | Path) -> list:

        reader = PdfReader(source)

        documents = []
        for page in reader.pages:
            text = page.extract_text()

            if text:
                documents.append(text)

        return documents


class DocumentLoaderService:

    def __init__(self, loader: BaseDocumentLoader):
        self.loader = loader

    def load_document(self, source: str | Path) -> list:
        return self.loader.load(source)