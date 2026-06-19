"""
Ingestion pipeline: read documents from ./data, chunk them, embed them,
and persist them into a local ChromaDB collection in ./db.

Run this once whenever you add or change documents in ./data:
    python -m src.ingest
"""

from tqdm import tqdm

from . import config
from .document_loader import load_all_documents
from .chunker import chunk_extracted_pages
from .vector_store import save_chunks


def run_ingestion(data_dir: str = config.DATA_DIR, db_dir: str = config.DB_DIR) -> None:
    print(f"[ingest] Scanning {data_dir} ...")
    pages = load_all_documents(data_dir)
    if not pages:
        print("[ingest] No readable documents found. Add PDFs/DOCX/TXT files to ./data and re-run.")
        return

    print(f"[ingest] Extracted {len(pages)} page-level text block(s). Chunking ...")
    chunks = chunk_extracted_pages(pages, chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)

    print(f"[ingest] Created {len(chunks)} chunk(s). Embedding + saving to {db_dir} ...")
    for _ in tqdm(range(1), desc="Indexing"):
        save_chunks(chunks, db_path=db_dir)

    print(f"[ingest] Done. Indexed {len(chunks)} chunks into the '{config.COLLECTION_NAME}' collection.")


if __name__ == "__main__":
    run_ingestion()
