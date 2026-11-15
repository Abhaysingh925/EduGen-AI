
"""Multi-format document ingestion pipeline for EduGen-AI Track A."""
from __future__ import annotations

import os
from typing import Any

from processors.pdf_processor import process_pdf
from processors.docx_processor import process_docx
from processors.pptx_processor import process_pptx
from utils.text_cleaner import clean_text, remove_repeated_lines
from utils.categorizer import categorize
from utils.chunker import chunk_document
from utils.code_analyzer import analyze_text

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx"}


def process_document(file: Any, chunk_size: int = 900, overlap: int = 120) -> list[dict]:
    """Extract, clean, analyse, classify and chunk a document."""

    name = os.path.basename(getattr(file, "name", str(file)))
    ext = os.path.splitext(name)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {ext or '(no extension)'}. "
            "Use PDF, DOCX, or PPTX."
        )

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
    doc["pages"] = [
        item for item in doc["pages"]
        if item.get("text", "").strip()
    ]

    sample_text = " ".join(
        item["text"] for item in doc["pages"][:3]
    )
    category = categorize(doc["filename"], sample_text)

    # Analyse complete pages before splitting them into chunks.
    page_analysis = {}

    for page in doc["pages"]:
        page_number = page["page"]
        analysis = analyze_text(page["text"])

        page_analysis[page_number] = {
            "contains_code": analysis["contains_code"],
            "code_blocks": analysis["code_blocks"],
            "programming_languages": list({
                block["detected_language"]
                for block in analysis["code_blocks"]
                if block["detected_language"] != "Unknown"
            }),
        }

    # Create normal text chunks for retrieval and RAG.
    chunks = chunk_document(
        doc["pages"],
        doc["filename"],
        category,
        chunk_size,
        overlap,
    )

    # Attach complete page-level code examples to only the first
    # chunk of each page, avoiding duplicate code displays.
    processed_pages = set()

    for chunk in chunks:
        chunk["file_type"] = ext.lstrip(".")
        chunk["location_type"] = location_type

        page_number = chunk["page"]

        chunk["contains_code"] = False
        chunk["code_blocks"] = []
        chunk["programming_languages"] = []

        if page_number not in processed_pages:
            analysis = page_analysis.get(page_number, {})

            chunk["contains_code"] = analysis.get(
                "contains_code", False
            )
            chunk["code_blocks"] = analysis.get(
                "code_blocks", []
            )
            chunk["programming_languages"] = analysis.get(
                "programming_languages", []
            )

            processed_pages.add(page_number)

    return chunks
