from pathlib import Path

import faiss
import json



class VectorStoreRepository:

    def __init__(self, index_path: Path, metadata_path: Path):

        self.index_path = index_path
        self.metadata_path = metadata_path


    def save_index(self, index: faiss.Index) -> None:

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(self.index_path))


    def load_index(self) -> faiss.Index:

        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Vector index not found: {self.index_path}"
            )

        return faiss.read_index(str(self.index_path))


    def save_metadata(self, metadata: list[dict]) -> None:

        self.doc_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.metadata_path, "w", encoding="utf-8") as file:
            json.dump(metadata, file, ensure_ascii=False, indent=4)


    def load_metadata(self):

        if not self.metadata_path.exists():
            raise FileNotFoundError(
                f"Metadata file not found: {self.metadata_path}"
            )

        with open(self.metadata_path, "r", encoding="utf-8") as file:
            return json.load(file)


    def exists(self) -> bool:
        return self.index_path.exists()
        