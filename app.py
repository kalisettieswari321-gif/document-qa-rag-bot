"""
Streamlit UI for the Document Q&A Bot.

Two tabs:
  1. Upload & Build Index — upload PDFs/DOCX/TXT and build/refresh the vector DB.
  2. Ask Questions — chat with your documents; grounded answers with citations.

Run locally:
    streamlit run app.py

Deploy for free on Streamlit Community Cloud (share.streamlit.io):
  1. Push this repo to GitHub.
  2. On share.streamlit.io, click "New app", point it at this repo, set main
     file to app.py.
  3. In the app's "Secrets" settings, add:
         GEMINI_API_KEY = "your_key_here"
  4. Deploy — you'll get a public https://...streamlit.app URL.
"""

import os
import shutil
import streamlit as st

from src import config
from src.document_loader import load_all_documents
from src.chunker import chunk_extracted_pages
from src.vector_store import save_chunks
from src.query import query_rag_pipeline

st.set_page_config(page_title="Document Q&A Bot", page_icon="📄", layout="wide")

# Streamlit Cloud secrets take priority; falls back to a local .env value
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass  # no secrets.toml present locally — that's fine, .env will be used

st.title("📄 Document Q&A Bot (RAG)")
st.caption(
    "Ask questions about your own PDF / DOCX / TXT documents — answers are "
    "grounded only in the content you upload, with source citations."
)

if not os.getenv("GEMINI_API_KEY"):
    st.error(
        "GEMINI_API_KEY is not set. Add it to a local .env file, or to this "
        "app's Secrets if deployed on Streamlit Community Cloud."
    )

tab_upload, tab_chat = st.tabs(["1️⃣ Upload & Build Index", "2️⃣ Ask Questions"])

with tab_upload:
    st.subheader("Upload documents")
    uploaded_files = st.file_uploader(
        "Upload one or more PDF / DOCX / TXT files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    if st.button("Build / Rebuild Index", type="primary", disabled=not uploaded_files):
        os.makedirs(config.DATA_DIR, exist_ok=True)
        for uploaded in uploaded_files:
            dest_path = os.path.join(config.DATA_DIR, uploaded.name)
            with open(dest_path, "wb") as f:
                f.write(uploaded.getbuffer())

        with st.spinner("Reading documents..."):
            pages = load_all_documents(config.DATA_DIR)
        with st.spinner("Chunking text..."):
            chunks = chunk_extracted_pages(pages, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        with st.spinner(f"Embedding {len(chunks)} chunk(s) and saving to the vector DB..."):
            save_chunks(chunks, db_path=config.DB_DIR)

        st.success(
            f"Indexed {len(chunks)} chunk(s) from {len(uploaded_files)} file(s). "
            "Switch to the 'Ask Questions' tab."
        )

    if os.path.isdir(config.DB_DIR) and os.listdir(config.DB_DIR):
        st.info("An index already exists. Uploading new files and rebuilding will add to it.")

    if st.button("Clear index"):
        if os.path.isdir(config.DB_DIR):
            shutil.rmtree(config.DB_DIR)
        st.warning("Index cleared. Upload documents and rebuild.")

with tab_chat:
    st.subheader("Ask a question about your documents")

    if not os.path.isdir(config.DB_DIR) or not os.listdir(config.DB_DIR):
        st.warning("No index found yet. Go to the 'Upload & Build Index' tab first.")
    else:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for role, content in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(content)

        user_query = st.chat_input("Ask something about your documents...")

        if user_query:
            st.session_state.chat_history.append(("user", user_query))
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                with st.spinner("Searching documents and generating a grounded answer..."):
                    result = query_rag_pipeline(user_query)
                answer = result["answer"]
                st.markdown(answer)
                if result["citations"]:
                    with st.expander("Sources"):
                        for c in result["citations"]:
                            st.markdown(f"- {c}")
            st.session_state.chat_history.append(("assistant", answer))
