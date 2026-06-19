# Document Q&A Bot — RAG with Gemini + ChromaDB

A Retrieval-Augmented Generation (RAG) system that answers questions about
your own PDF/DOCX/TXT documents, grounded strictly in their content, with
inline source citations (filename + page number).

Live demo: **[add your deployed Streamlit URL here]**

---

## 1. How it works

```
 Documents (PDF/DOCX/TXT)
          │
          ▼
 Extract text + track source/page  ──▶  Split into overlapping chunks
          │                                        │
          ▼                                        ▼
   Embed each chunk (Gemini text-embedding-004) ──▶ Store in ChromaDB (./db)

 User question
          │
          ▼
  Embed question (same model) ──▶ Retrieve top-k similar chunks from ChromaDB
          │                                  │
          ▼                                  ▼
  Build a grounded prompt (context + citations) ──▶ Gemini generates the answer
                          │
                          ▼
                 Answer + cited sources
```

This solves two well-known LLM limitations:
- **No access to private/recent documents** — the model only ever sees text
  pulled from *your* files, supplied at query time.
- **Hallucination** — the system prompt instructs the model to answer using
  only the retrieved context, and to say so explicitly when an answer isn't
  in the documents.

## 2. Project structure

```
document-qa-bot/
├── .env.example          # Template for your API key — copy to .env
├── .gitignore
├── README.md              # This file
├── requirements.txt
├── app.py                 # Streamlit UI (upload docs + chat) — for deployment
├── data/                  # Your source documents go here
│   ├── business_doc.pdf   # Sample: fictional retail company report
│   ├── science_paper.pdf  # Sample: fictional research summary
│   ├── factsheet.docx     # Sample: fictional product factsheet
│   └── faq.txt            # Sample: fictional customer FAQ
├── db/                    # Persistent ChromaDB storage (created by ingest)
└── src/
    ├── __init__.py
    ├── config.py          # All tunable constants in one place
    ├── document_loader.py # PDF / DOCX / TXT text extraction
    ├── chunker.py          # Overlapping character-window chunking
    ├── vector_store.py     # ChromaDB persistence + embedding function
    ├── ingest.py           # Script: build/refresh the vector index
    ├── query.py            # Core retrieval + grounded generation logic
    └── main.py             # Interactive CLI chat loop
```

## 3. Setup

```bash
git clone <your-repo-url>
cd document-qa-bot

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # then paste your Gemini API key into .env
```

Get a free Gemini API key at [Google AI Studio](https://aistudio.google.com/app/apikey).

## 4. Usage

**Add your documents** (4–5 files: PDFs and/or a DOCX) into `data/`, replacing
the sample file.

**Build the index** (run once, and again any time documents change):
```bash
python -m src.ingest
```

**Ask questions from the terminal:**
```bash
python -m src.main
```

**Or launch the web UI:**
```bash
streamlit run app.py
```

## 5. Deploying the live demo (free — Streamlit Community Cloud)

1. Push this repo to GitHub (make sure `.env` and `db/` are *not* committed —
   `.gitignore` already excludes them).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app** →
   select your repo and branch, set the main file to `app.py`.
3. In **Advanced settings → Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your_key_here"
   ```
4. Deploy. You'll get a public `https://<your-app>.streamlit.app` URL — use
   the "Upload & Build Index" tab there to index your documents on first
   load (the free tier's filesystem isn't permanent across deploys, so the
   index is rebuilt from uploads each time the app restarts).

## 6. Design decisions (analysis)

- **Chunk size (1000 chars) / overlap (200 chars):** Large enough to keep a
  paragraph's worth of context per chunk, small enough to avoid pulling in
  irrelevant text and wasting tokens. The overlap protects facts that land
  right on a chunk boundary.
- **ChromaDB over a hosted vector DB:** Needed zero server setup, persists
  to a local folder, and is free — ideal for a small, single-user document
  set like this one.
- **Gemini for both embeddings and generation:** One vendor, one API key,
  and a generous free tier — minimizes setup friction.
- **Strict grounding in the system prompt:** Explicitly instructs the model
  to answer only from retrieved context and to say so when it can't find an
  answer, rather than guessing.
- **Per-chunk metadata (source filename + page number):** Carried through
  every stage so the final answer can cite exactly where each fact came
  from.

## 7. Limitations & possible improvements

- Chunking is purely character-based, not sentence/paragraph-aware — a
  smarter recursive splitter (cutting on `\n\n`, then `\n`, then spaces)
  would preserve sentence boundaries better.
- No re-ranking step — all top-k results are used as-is rather than
  filtered by a relevance-score threshold.
- DOCX files are treated as one block (no real page numbers); a
  paragraph/heading-based "page" approximation could be added.
- No conversation memory — each question is answered independently of
  previous turns.
- No automated evaluation harness (e.g. a fixed set of test questions with
  expected answers) to measure retrieval/answer quality over time.

## 8. Tech stack

Python 3.11+, `pypdf`, `python-docx`, `chromadb`, `google-generativeai`
(Gemini `text-embedding-004` + `gemini-2.5-flash-preview-09-2025`),
`python-dotenv`, `tqdm`, `streamlit`.
