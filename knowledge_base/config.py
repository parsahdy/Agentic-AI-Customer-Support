from pathlib import Path

#3 Chnking
CHUNKER = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
}
CHUNKER_TYPE="recursive"

## Embedding
SENTENCE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BGE_MODEL = "BAAI/bge-m3"
EMBEDDING_TYPE="sentence"

## Vector store
VECTOR_STORE_TYPE="faiss"

## retriever
K = 5
SCORE = int
THRESHOLD = int
RETRIEVER_TYPE="vector"

## Directories
PROJECT_ROOT = Path(__file__).resolve().parents[1]
KB_DIR = PROJECT_ROOT / "data" / "knowledge_base" 
INDEX_PATH = KB_DIR / "vector_index.faiss"
METADATA_PATH = KB_DIR / "vector_metadata.json"
INPUT_DIR = PROJECT_ROOT / "data" / "cleaned"
PDF_DIR = PROJECT_ROOT / "data" / "pdf"