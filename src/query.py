"""
Query pipeline: embed the user's question, retrieve the closest chunks from
ChromaDB, build a strictly-grounded prompt, and ask Gemini to answer.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

from . import config
from .vector_store import get_collection

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = (
    "You are a professional, accurate document Q&A assistant. "
    "Answer the user's question using ONLY the provided document context below. "
    "Cite the sources (filenames and pages) inline next to facts you mention, "
    "e.g. (report.pdf, Page 4). "
    "If the answer cannot be found in the context, clearly state: "
    "'I am sorry, but the provided documents do not contain the answer to your question.' "
    "Do not make up facts or use external knowledge."
)


def query_rag_pipeline(user_query: str, db_path: str = config.DB_DIR, k: int = config.TOP_K) -> dict:
    """Search the database, build a grounded prompt, and query the LLM."""
    if not API_KEY:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # pick up keys set after import (e.g. Streamlit)

    collection = get_collection(db_path=db_path)
    results = collection.query(query_texts=[user_query], n_results=k)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    context_blocks = []
    citations = []

    for doc, meta in zip(documents, metadatas):
        source_name = meta.get("source", "unknown")
        page_num = meta.get("page", "N/A")
        citation_str = f"Source: {source_name}, Page: {page_num}"
        context_blocks.append(f"[{citation_str}]\nContext: {doc}")
        citations.append(citation_str)

    if not context_blocks:
        return {
            "answer": "I am sorry, but the provided documents do not contain the answer to your question.",
            "citations": [],
            "raw_context": [],
        }

    context_payload = "\n\n---\n\n".join(context_blocks)

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"CONTEXT INFORMATION:\n{context_payload}\n\n"
        f"USER QUESTION: {user_query}\n\n"
        f"GROUNDED ANSWER:"
    )

    model = genai.GenerativeModel(config.GENERATION_MODEL)
    response = model.generate_content(prompt)

    return {
        "answer": response.text,
        "citations": citations,
        "raw_context": documents,
    }
