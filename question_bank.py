
"""Source-grounded question bank generator for EduGen-AI."""
from __future__ import annotations

import json
import os
import re
from typing import Any


def generate_question_bank(
    topic: str,
    results: list[dict[str, Any]],
    mcq_count: int = 5,
    short_count: int = 3,
    long_count: int = 2,
    difficulty: str = "Mixed",
    api_key: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """Generate questions from retrieved study material using Gemini."""

    if not results:
        raise ValueError(
            "No source passages found. Upload study material and search again."
        )

    # Limit context size and preserve source references.
    evidence_parts = []
    for i, item in enumerate(results, start=1):
        source = item.get("source", "Unknown source")
        page = item.get("page", "?")
        category = item.get("category", "Other")
        text = str(item.get("text", "")).strip()

        if text:
            evidence_parts.append(
                f"[Source {i}: {source}; page/slide {page}; "
                f"category {category}]\n{text[:5000]}"
            )

    if not evidence_parts:
        raise ValueError("Retrieved passages contain no usable text.")

    evidence = "\n\n".join(evidence_parts)[:24000]
    key = (api_key or os.getenv("GEMINI_API_KEY", "")).strip()

    if not key:
        raise RuntimeError(
            "Gemini API key is not configured. Set GEMINI_API_KEY "
            "in your environment or Streamlit Secrets."
        )

    from google import genai

    client = genai.Client(api_key=key)
    model_name = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    prompt = f"""
You are an academic question-paper creator.
Use ONLY the supplied study-material excerpts.

TOPIC: {topic}
DIFFICULTY: {difficulty}
NUMBER OF MCQs: {mcq_count}
NUMBER OF SHORT-ANSWER QUESTIONS: {short_count}
NUMBER OF LONG-ANSWER QUESTIONS: {long_count}

Create questions that test understanding, not just memorisation.
Every MCQ must have exactly four options labelled A, B, C, D.
Give the correct answer and a brief explanation for every question.
For short and long answers, give a model answer or solution.
Attach source references using the supplied source labels.
Do not invent facts that are not supported by the excerpts.
If the excerpts do not support enough questions, return fewer questions
rather than making up information.

Return ONLY valid JSON in this format:
{{
  "topic": "{topic}",
  "difficulty": "{difficulty}",
  "mcqs": [
    {{
      "question": "Question text",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "answer": "A",
      "explanation": "Why this is correct",
      "source": "Source 1"
    }}
  ],
  "short_questions": [
    {{
      "question": "Question text",
      "answer": "Model answer",
      "source": "Source 1"
    }}
  ],
  "long_questions": [
    {{
      "question": "Question text",
      "answer": "Step-by-step model answer",
      "source": "Source 1"
    }}
  ]
}}

STUDY MATERIAL:
{evidence}
"""

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    raw = (getattr(response, "text", None) or "").strip()
    if not raw:
        raise RuntimeError("Gemini returned an empty response.")

    # Handle JSON enclosed in Markdown code fences.
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        bank = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned invalid JSON. Please generate the bank again."
        ) from exc

    for field in ("mcqs", "short_questions", "long_questions"):
        if not isinstance(bank.get(field), list):
            raise RuntimeError(f"Invalid question-bank format: {field}")

    bank["topic"] = topic
    bank["difficulty"] = difficulty
    return bank
