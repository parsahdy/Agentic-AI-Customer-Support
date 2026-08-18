from pathlib import Path

from .document_loader import (
    BaseDocumentLoader,
    CSVDocumentLoader,
    ExcelDocumentLoader,
    JSONDocumentLoader,
    PDFDocumentLoader,
)



class LoaderFactory:

    _loaders: dict[str, type[BaseDocumentLoader]] = {
        "csv": CSVDocumentLoader,
        "excel": ExcelDocumentLoader,
        "xlsx": ExcelDocumentLoader,
        "xls": ExcelDocumentLoader,
        "json": JSONDocumentLoader,
        "pdf": PDFDocumentLoader,
    }

    @classmethod
    def create(cls, loader_type: str):

        loader_type = loader_type.lower().strip()

        if loader_type not in cls._loaders:
            raise ValueError(
                f"Unsupported document type: {loader_type}."
                f"Supported loader type: {list(cls._loaders.keys())}"
            )

        loader_class = cls._loaders[loader_type]

        return loader_class()

    @classmethod
    def create_from_path(cls, source: str | Path) -> BaseDocumentLoader:

        source = Path(source)
        extension = source.suffix.lower().lstrip(".")
        return cls.create(extension)