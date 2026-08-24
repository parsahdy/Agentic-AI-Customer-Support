import json
from pathlib import Path
from typing import Any



class KnowledgeBaseVersion:

    def __init__(self, version_path: Path):
        self.version_path = version_path

    def create(
        self,
        version: str,
        created_at: str,
        embedding_model: str,
        chunker_type: str,
        chunk_size: int,
        chunk_overlap: int,
        vector_store_type: str,
        document_count: int,
        chunk_count: int,
        embedding_dimension: int,
    ) -> dict[str, Any]:

        return {
                "version": version,
                "created_at": created_at,
                "embedding_model": embedding_model,
                "chunker_type": chunker_type,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "vector_store": vector_store_type,
                "document_count": document_count,
                "chunk_count": chunk_count,
                "embedding_dimension": embedding_dimension,
            }

    def save(self, version_data: dict[str, Any]) -> None:

        self.version_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.version_path, "w", encoding="utf-8") as file:
            json.dump(version_data, file, ensure_ascii=True, indent=4)

