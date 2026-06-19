"""Character-window chunking with overlap, carrying metadata through to every chunk."""


def chunk_extracted_pages(pages: list[dict], chunk_size: int = 1000, chunk_overlap: int = 200) -> list[dict]:
    """
    Splits page-level text blocks into smaller overlapping chunks.

    Why overlap matters: if a key fact sits right on a cut boundary, the
    overlap window ensures it still appears whole in at least one chunk.
    """
    chunks = []

    for page in pages:
        text = page["text"]
        metadata = page["metadata"]
        text_length = len(text)
        start = 0

        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk_text = text[start:end]

            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": metadata["source"],
                    "page": metadata["page"],
                    "chunk_range": f"{start}-{end}",
                },
            })

            next_start = start + (chunk_size - chunk_overlap)
            if next_start <= start:  # safety net if overlap >= chunk_size
                next_start = start + chunk_size
            start = next_start

    return chunks
