"""Split text into chunks and attach metadata."""


def split_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list:
    """Split on paragraph/sentence boundaries when possible."""
    text = text.strip()
    if not text:
        return []
    chunks, start = [], 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            # try to cut at a paragraph, then sentence, then space
            for sep in ("\n", ". ", " "):
                cut = text.rfind(sep, start + chunk_size // 2, end)
                if cut != -1:
                    end = cut + len(sep)
                    break
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def chunk_document(pages: list, source: str, category: str,
                   chunk_size: int = 800, overlap: int = 100) -> list:
    """pages: [{'page': n, 'text': '...'}]  (page = page OR slide number)
    Returns list of dicts: text, source, category, page, chunk_id"""
    result = []
    for p in pages:
        for piece in split_text(p["text"], chunk_size, overlap):
            result.append({
                "chunk_id": len(result) + 1,
                "text": piece,
                "source": source,
                "category": category,
                "page": p["page"],
            })
    return result
