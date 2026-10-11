"""Grounded academic explanation prompts, formatted with LangChain Core."""
from __future__ import annotations

try:
    from langchain_core.prompts import PromptTemplate
except Exception:  # development fallback before dependencies are installed
    class PromptTemplate:  # type: ignore[no-redef]
        def __init__(self, template: str):
            self.template = template

        @classmethod
        def from_template(cls, template: str):
            return cls(template)

        def format(self, **kwargs) -> str:
            return self.template.format(**kwargs)

EXPLANATION_TEMPLATE = """You are EduGen-AI, a careful academic tutor.
Explain the student's topic using ONLY the source excerpts supplied below.
If the sources do not contain enough evidence, clearly say what is missing rather than inventing facts.
Use the requested language and learning level. Make the explanation useful for a college student.
Structure the response with:
1. Topic overview
2. Step-by-step explanation
3. Important terms / examples
4. Exam-ready key points
5. Short recap
Cite factual claims using the source IDs in square brackets, e.g. [S1] or [S2].
Do not invent page numbers or sources. Avoid repeating the same fact unnecessarily.

Student topic: {question}
Learning level: {level}
Response language: {language}

Retrieved source excerpts:
{context}

Write the grounded explanation now."""

EXPLANATION_PROMPT = PromptTemplate.from_template(EXPLANATION_TEMPLATE)


def build_explanation_prompt(question: str, results: list[dict], language: str = "English", level: str = "College beginner") -> str:
    pieces = []
    for idx, item in enumerate(results, 1):
        location_label = item.get("location_type", "page")
        location_value = item.get("page", "?")
        pieces.append(
            f"[S{idx}] Source: {item.get('source', 'Unknown')}; "
            f"Category: {item.get('category', 'Other')}; "
            f"{location_label.title()}: {location_value}\n"
            f"Excerpt: {item.get('text', '')}"
        )
    return EXPLANATION_PROMPT.format(
        question=question,
        level=level,
        language=language,
        context="\n\n---\n\n".join(pieces),
    )
