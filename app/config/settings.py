from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

RAW_DATA = DATA_DIR / "raw"

VECTOR_STORE = DATA_DIR / "vector_store" / "aviation_v1"

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200

EMBEDDING_MODEL = "sentence-transformers/all-Mini-L6-v2"

TOP_K = 5