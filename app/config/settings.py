from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

RAW_DATA = DATA_DIR / "raw"

# UPLOAD_DIR = DATA_DIR / "uploads"

# METADATA_DIR = DATA_DIR / "metadata"

# AVIATION_INDEX_DIR = VECTOR_STORE_DIR / "aviation_index"

# UPLOADED_INDEX_DIR = VECTOR_STORE_DIR / "uploaded_index"

VECTOR_STORE = DATA_DIR / "vector_store" / "aviation_v1"

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

TOP_K = 5

FETCH_K = 40

MMR_LAMBDA = 0.85