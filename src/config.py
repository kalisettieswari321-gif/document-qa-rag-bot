"""
Central configuration for the Document Q&A RAG bot.
Keeping every tunable value in one place makes the system easy to adjust
without hunting through ingest.py / query.py / main.py.
"""

import os

# ---- Paths -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_DIR = os.path.join(BASE_DIR, "db")

# ---- Chunking ------------------------------------------------------------
CHUNK_SIZE = 1000        # characters per chunk
CHUNK_OVERLAP = 200      # overlap between consecutive chunks

# ---- Retrieval -------------------------------------------------------------
TOP_K = 4                # number of chunks retrieved per query

# ---- Models ------------------------------------------------------------------
# NOTE: If these exact model identifiers are unavailable on your account/region,
# swap them for the current equivalents listed at https://ai.google.dev/gemini-api/docs/models
EMBEDDING_MODEL = "models/gemini-embedding-001"
GENERATION_MODEL = "models/gemini-3.5-flash"
# ---- ChromaDB ------------------------------------------------------------------
COLLECTION_NAME = "document_knowledge_base"

SUPPORTED_EXTENSIONS = (".pdf", ".docx", ".txt")
