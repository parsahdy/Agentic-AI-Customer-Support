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

    def load(self, source: str | Path) -> list[dict]:

        document = []
        for pdf in source.glob("*.pdf"):
            reader = PdfReader(pdf)

            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""

                document.append(
                    {
                        "page_content": text,
                        "metadata": {
                            "page_number": page_number,
                            "filename": pdf.name,
                            "source": str(pdf)
                        }
                    }
                )

        return document