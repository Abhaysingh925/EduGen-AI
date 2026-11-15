import os
from PyPDF2 import PdfReader


def process_pdf(file) -> dict:
    """file = path string OR uploaded file object (Streamlit)."""
    filename = os.path.basename(getattr(file, "name", file))
    reader = PdfReader(file)
    pages, empty = [], []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if not text:          # empty / scanned page
            empty.append(i)
            continue
        pages.append({"page": i, "text": text})
    return {"filename": filename, "type": "pdf", "pages": pages, "empty_pages": empty}
