This folder holds your source documents (PDF / DOCX / TXT).

4 sample documents are included so the pipeline works immediately:
  business_doc.pdf   — fictional retail company annual report
  science_paper.pdf  — fictional agricultural research summary
  factsheet.docx      — fictional product factsheet
  faq.txt             — fictional customer FAQ

Delete these and drop in your own files any time — just re-run `python -m src.ingest` afterward.

(This file is named with a leading underscore and .md extension on purpose,
so the ingestion pipeline — which only reads .pdf/.docx/.txt — skips it.)
