"""
Document loading utilities.
Each extractor returns a list of dicts: {"text": str, "metadata": {...}}
so that every downstream chunk can be traced back to its source file
(and page number, for PDFs).
"""

import os
from pypdf import PdfReader
from docx import Document


def extract_pdf_pages(file_path: str) -> list[dict]:
    """Extract text page-by-page from a PDF, tracking page numbers."""
    extracted = []
    file_name = os.path.basename(file_path)
    try:
        reader = PdfReader(file_path)
        for index, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                clean_text = " ".join(text.split())
                extracted.append({
                    "text": clean_text,
                    "metadata": {"source": file_name, "page": index + 1},
                })
    except Exception as e:
        print(f"[ingest] Error reading PDF {file_name}: {e}")
    return extracted


def extract_docx_pages(file_path: str) -> list[dict]:
    """
    Extract text from a Word document.

    .docx has no fixed page boundaries until it's actually rendered/printed,
    so the whole document is treated as a single logical block (page="N/A").
    The chunker still splits this block into smaller overlapping pieces.
    """
    extracted = []
    file_name = os.path.basename(file_path)
    try:
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        full_text = " ".join(" ".join(paragraphs).split())
        if full_text:
            extracted.append({
                "text": full_text,
                "metadata": {"source": file_name, "page": "N/A"},
            })
    except Exception as e:
        print(f"[ingest] Error reading DOCX {file_name}: {e}")
    return extracted


def extract_txt_file(file_path: str) -> list[dict]:
    """Extract text from a plain .txt file (bonus format, not required by the spec)."""
    extracted = []
    file_name = os.path.basename(file_path)
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = " ".join(f.read().split())
        if text:
            extracted.append({
                "text": text,
                "metadata": {"source": file_name, "page": "N/A"},
            })
    except Exception as e:
        print(f"[ingest] Error reading TXT {file_name}: {e}")
    return extracted


def load_all_documents(data_dir: str) -> list[dict]:
    """Walk the data directory and dispatch each file to the right extractor."""
    all_pages = []
    if not os.path.isdir(data_dir):
        print(f"[ingest] Data directory not found: {data_dir}")
        return all_pages

    for file_name in sorted(os.listdir(data_dir)):
        file_path = os.path.join(data_dir, file_name)
        if not os.path.isfile(file_path):
            continue
        lower = file_name.lower()
        if lower.endswith(".pdf"):
            all_pages.extend(extract_pdf_pages(file_path))
        elif lower.endswith(".docx"):
            all_pages.extend(extract_docx_pages(file_path))
        elif lower.endswith(".txt"):
            all_pages.extend(extract_txt_file(file_path))
        else:
            print(f"[ingest] Skipping unsupported file: {file_name}")
    return all_pages
