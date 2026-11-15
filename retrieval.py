"""Lightweight topic retrieval: LangChain Documents + TF-IDF vectors + FAISS.

TF-IDF is intentionally used for this Week 1-2 MVP: it avoids downloading a
large embedding model and is practical on a low-memory student laptop. FAISS
performs the nearest-neighbour search. A scikit-learn fallback is provided in
case FAISS cannot be imported in a local environment.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

try:
    import faiss  # type: ignore
    HAS_FAISS = True
except Exception:  # pragma: no cover - depends on platform install
    faiss = None
    HAS_FAISS = False

try:
    from langchain_core.documents import Document
except Exception:  # allows the basic retriever to be tested before installing deps
    class Document:  # type: ignore[no-redef]
        def __init__(self, page_content: str, metadata: dict | None = None):
            self.page_content = page_content
            self.metadata = metadata or {}


def _make_document(chunk: dict[str, Any]) -> Document:
    metadata = {k: v for k, v in chunk.items() if k != "text"}
    return Document(page_content=str(chunk.get("text", "")), metadata=metadata)


def search_chunks(
    chunks: list[dict[str, Any]],
    query: str,
    top_k: int = 6,
    category: str = "All",
    diversify_sources: bool = True,
    subject: str = "All",
    chapter: str = "All",
) -> list[dict[str, Any]]:
    """Return the most relevant chunks, preserving source/category/page metadata."""
    query = (query or "").strip()
    if not query or not chunks:
        return []


    candidates = [c for c in chunks if str(c.get("text", "")).strip()]

    if category and category != "All":
        candidates = [
            c for c in candidates
            if c.get("category", "Other") == category
        ]

    if subject and subject != "All":
        candidates = [
            c for c in candidates
            if c.get("subject", "Unassigned") == subject
        ]

    if chapter and chapter != "All":
        candidates = [
            c for c in candidates
            if c.get("chapter", "Unassigned") == chapter
        ]
    if not candidates:
        return []

    docs = [_make_document(c) for c in candidates]
    corpus = [d.page_content for d in docs]
    vectorizer = TfidfVectorizer(
        lowercase=True,
        strip_accents="unicode",
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
        max_features=4096,
        token_pattern=r"(?u)\b\w\w+\b",
    )
    try:
        matrix = vectorizer.fit_transform(corpus)
        query_vector = vectorizer.transform([query])
    except ValueError:  # e.g. all documents consist only of stop words
        return []
    if query_vector.nnz == 0:
        return []

    # TF-IDF vectors are normalised, so inner product represents cosine similarity.
    dense = normalize(matrix, norm="l2", copy=True).toarray().astype("float32", copy=False)
    q_dense = normalize(query_vector, norm="l2", copy=True).toarray().astype("float32", copy=False)

    scored: list[tuple[float, int]] = []
    if HAS_FAISS and dense.shape[1] > 0:
        index = faiss.IndexFlatIP(int(dense.shape[1]))
        index.add(dense)
        scores, ids = index.search(q_dense, len(candidates))
        scored = [(float(score), int(idx)) for score, idx in zip(scores[0], ids[0]) if idx >= 0]
    else:
        scores = (dense @ q_dense.T).reshape(-1)
        scored = [(float(score), i) for i, score in enumerate(scores)]
        scored.sort(reverse=True)

    scored = [(score, idx) for score, idx in scored if score > 0.015]
    selected: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    source_counts: dict[str, int] = defaultdict(int)
    # With multiple uploaded files, avoid letting a single long document crowd out
    # every other source. Backfill any remaining slots after the first pass.
    for score, idx in scored:
        chunk = dict(candidates[idx])
        chunk["score"] = round(score, 4)
        source = str(chunk.get("source", "Unknown source"))
        if diversify_sources and source_counts[source] >= max(2, math.ceil(top_k / 2)):
            deferred.append(chunk)
            continue
        selected.append(chunk)
        source_counts[source] += 1
        if len(selected) >= top_k:
            break
    if len(selected) < top_k:
        already = {(c.get("source"), c.get("page"), c.get("chunk_id")) for c in selected}
        for chunk in deferred:
            key = (chunk.get("source"), chunk.get("page"), chunk.get("chunk_id"))
            if key not in already:
                selected.append(chunk)
                already.add(key)
                if len(selected) >= top_k:
                    break
    return selected


def retrieval_engine_name() -> str:
    return "FAISS vector search" if HAS_FAISS else "scikit-learn cosine-similarity fallback"
