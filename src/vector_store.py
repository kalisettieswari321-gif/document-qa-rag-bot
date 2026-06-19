"""ChromaDB persistence helpers shared by ingest.py, query.py, and app.py."""

import os
import chromadb
from chromadb.utils.embedding_functions import GoogleGenerativeAiEmbeddingFunction
from dotenv import load_dotenv

from . import config

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")


def get_embedding_function():
    key = os.getenv("GEMINI_API_KEY")  # re-read in case it was set after import (e.g. Streamlit secrets)
    if not key:
        raise EnvironmentError(
            "GEMINI_API_KEY is not set. Add it to a .env file, your environment, "
            "or Streamlit secrets."
        )
    return GoogleGenerativeAiEmbeddingFunction(
        api_key=key,
        model_name=config.EMBEDDING_MODEL,
    )


def get_collection(db_path: str = config.DB_DIR, create: bool = False):
    client = chromadb.PersistentClient(path=db_path)
    embedding_fn = get_embedding_function()

    if create:
        return client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            embedding_function=embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )
    return client.get_collection(
        name=config.COLLECTION_NAME,
        embedding_function=embedding_fn,
    )


def save_chunks(chunks: list[dict], db_path: str = config.DB_DIR, batch_size: int = 100) -> int:
    """Embed and persist chunks into ChromaDB, in batches to keep requests small."""
    collection = get_collection(db_path=db_path, create=True)

    for batch_start in range(0, len(chunks), batch_size):
        batch = chunks[batch_start: batch_start + batch_size]
        ids = [f"id_{batch_start + i}" for i in range(len(batch))]
        documents = [c["text"] for c in batch]
        metadatas = [c["metadata"] for c in batch]
        collection.add(ids=ids, documents=documents, metadatas=metadatas)

    return len(chunks)
