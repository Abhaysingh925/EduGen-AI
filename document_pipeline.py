"""Multi-format document ingestion pipeline for EduGen-AI Track A."""
from __future__ import annotations

import os
from typing import Any, BinaryIO

from processors.pdf_processor import process_pdf
from processors.docx_processor import process_docx
from processors.pptx_processor import process_pptx
from utils.text_cleaner import clean_text, remove_repeated_lines
from utils.categorizer import categorize
from utils.chunker import chunk_document
from utils.code_analyzer import analyze_text
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx"}


def process_document(file: Any, chunk_size: int = 900, overlap: int = 120) -> list[dict]:
    """Extract text, clean it, classify the source, and return metadata-rich chunks.

    `file` can be a filesystem path or a file-like object such as Streamlit's
    UploadedFile. `page` means PDF page, PPTX slide, or an approximate DOCX
    paragraph group (Word does not expose stable page boundaries through python-docx).
    """
    name = os.path.basename(getattr(file, "name", str(file)))
    ext = os.path.splitext(name)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext or '(no extension)'}. Use PDF, DOCX, or PPTX.")

    # File-like objects can be reused; rewind before parsing where possible.
    try:
        file.seek(0)
    except (AttributeError, OSError):
        pass

    if ext == ".pdf":
        doc = process_pdf(file)
        location_type = "page"
    elif ext == ".docx":
        doc = process_docx(file)
        location_type = "section"
    else:
        doc = process_pptx(file)
        location_type = "slide"

    for item in doc["pages"]:
        item["text"] = clean_text(item.get("text", ""))
    doc["pages"] = remove_repeated_lines(doc["pages"])
    doc["pages"] = [item for item in doc["pages"] if item.get("text", "").strip()]

    sample_text = " ".join(item["text"] for item in doc["pages"][:3])
    category = categorize(doc["filename"], sample_text)
    chunks = chunk_document(doc["pages"], doc["filename"], category, chunk_size, overlap)

    for chunk in chunks:
        chunk["file_type"] = ext.lstrip(".")
        chunk["location_type"] = location_type

        analysis = analyze_text(chunk["text"])
        chunk["contains_code"] = analysis["contains_code"]
        chunk["code_blocks"] = analysis["code_blocks"]
        chunk["programming_languages"] = list({
            block["detected_language"]
            for block in analysis["code_blocks"]
            if block["detected_language"] != "Unknown"
        })

    return chunks
