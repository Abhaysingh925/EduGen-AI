"""Gemini generation with a clearly labelled extractive fallback."""
from __future__ import annotations

import os
import re
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from prompts import build_explanation_prompt

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text or "")
    return [p.strip(" •\t-") for p in parts if len(p.strip()) >= 35]


def local_evidence_explanation(question: str, results: list[dict[str, Any]], language: str = "English") -> str:
    """Build a source-grounded, extractive mini-explanation without an API key."""
    if not results:
        return "No matching source passages were found. Try a more specific topic or upload more material."

    q_words = {w.lower() for w in re.findall(r"[a-zA-Z0-9]{2,}", question)}
    scored: list[tuple[float, str, dict[str, Any]]] = []
    seen = set()
    for result in results:
        for sentence in _sentences(str(result.get("text", ""))):
            normalized = re.sub(r"\W+", " ", sentence.lower()).strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            words = set(re.findall(r"[a-zA-Z0-9]{2,}", normalized))
            overlap = len(words & q_words)
            score = overlap + min(len(sentence) / 300, 0.4) + float(result.get("score", 0))
            scored.append((score, sentence, result))
    scored.sort(key=lambda row: row[0], reverse=True)
    chosen = scored[:8]
    if not chosen:
        chosen = [(0.0, str(r.get("text", "")).strip(), r) for r in results[:4] if str(r.get("text", "")).strip()]

    if language.lower().startswith("hindi"):
        title, overview, keys, recap = "## Vishay ka saar", "Uploaded material ke aadhar par:", "## Zaroori baatein", "## Quick revision"
    elif language.lower().startswith("hinglish"):
        title, overview, keys, recap = "## Topic ka overview", "Uploaded study material ke basis par:", "## Important points", "## Quick revision"
    else:
        title, overview, keys, recap = "## Topic overview", "Based on the uploaded study material:", "## Key points from your sources", "## Quick revision"

    lines = [title, f"**{question.strip()}**", "", overview, ""]
    for i, (_, sentence, result) in enumerate(chosen[:3], 1):
        src = result.get("source", "source")
        loc_type = result.get("location_type", "page")
        loc = result.get("page", "?")
        lines.append(f"{i}. {sentence} ([{src}, {loc_type} {loc}])")
    lines += ["", keys]
    for _, sentence, result in chosen[3:8]:
        src = result.get("source", "source")
        loc_type = result.get("location_type", "page")
        loc = result.get("page", "?")
        lines.append(f"- {sentence} ([{src}, {loc_type} {loc}])")
    lines += ["", recap, "- Review the key terms and examples in the cited excerpts.", "- Compare what the notes, textbook, questions, and/or lab material say about this topic."]
    return "\n".join(lines)


def explain_topic(
    question: str,
    results: list[dict[str, Any]],
    api_key: str | None = None,
    language: str = "English",
    level: str = "College beginner",
    model: str | None = None,
) -> dict[str, str]:
    """Return {answer, mode, notice}. Uses Gemini if a key works, else extractive mode."""
    key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()
    if key:
        try:
            from google import genai
            client = genai.Client(api_key=key)
            prompt = build_explanation_prompt(question, results, language, level)
            response = client.models.generate_content(
                model=model or DEFAULT_MODEL,
                contents=prompt,
            )
            answer = getattr(response, "text", None)
            if answer and answer.strip():
                return {"answer": answer.strip(), "mode": "Gemini grounded explanation", "notice": ""}
            raise RuntimeError("The model returned an empty response.")
        except Exception as exc:
            fallback = local_evidence_explanation(question, results, language)
            return {
                "answer": fallback,
                "mode": "Source-excerpt fallback",
                "notice": f"Gemini generation failed ({type(exc).__name__}). Showing source-based excerpts instead.",
            }
    return {
        "answer": local_evidence_explanation(question, results, language),
        "mode": "Source-excerpt mode (no API key)",
        "notice": "For a generated step-by-step AI explanation, add GEMINI_API_KEY in Streamlit Cloud Secrets or your local .env file. Current answer is based on retrieved source excerpts.",
    }
