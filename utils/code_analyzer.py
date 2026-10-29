
"""Basic programming language and code-block detection for EduGen-AI."""

from __future__ import annotations

import re
from typing import Any


LANGUAGE_PATTERNS = {
    "Python": [
        r"^\s*def\s+\w+\s*\(",
        r"^\s*class\s+\w+.*:",
        r"^\s*(if|elif|else|for|while|try|except|with)\b.*:",
        r"^\s*import\s+\w+",
        r"^\s*print\s*\(",
    ],
    "Java": [
        r"\bpublic\s+static\s+void\s+main\s*\(",
        r"\bSystem\.out\.println\s*\(",
        r"\bpublic\s+class\s+\w+",
        r"\bprivate\s+(static\s+)?(int|String|double|boolean)\b",
    ],
    "C++": [
        r"#include\s*<\w+>",
        r"\bint\s+main\s*\(",
        r"\bstd::cout\b",
        r"\bstd::cin\b",
        r"\busing\s+namespace\s+std\b",
    ],
}


def detect_language(code: str) -> dict[str, Any]:
    """Estimate the programming language using recognizable code patterns."""
    if not code or not code.strip():
        return {"language": "Unknown", "confidence": "low"}

    scores = {
        language: sum(
            bool(re.search(pattern, code, re.MULTILINE))
            for pattern in patterns
        )
        for language, patterns in LANGUAGE_PATTERNS.items()
    }

    best_language = max(scores, key=scores.get)
    best_score = scores[best_language]

    if best_score == 0:
        return {"language": "Unknown", "confidence": "low"}

    tied = sum(score == best_score for score in scores.values()) > 1
    confidence = "low" if tied or best_score == 1 else "medium"

    return {
        "language": "Unknown" if tied else best_language,
        "confidence": confidence,
    }


def extract_code_blocks(text: str) -> list[dict[str, Any]]:
    """Extract fenced Markdown code blocks while preserving their content."""
    blocks = []

    pattern = re.compile(
        r"```([^\n`]*)\n(.*?)```",
        re.DOTALL,
    )

    for match in pattern.finditer(text or ""):
        declared_language = match.group(1).strip()
        code = match.group(2)

        detection = detect_language(code)

        blocks.append({
            "code": code,
            "declared_language": declared_language or "Not specified",
            "detected_language": detection["language"],
            "confidence": detection["confidence"],
        })

    return blocks



def analyze_text(text: str) -> dict[str, Any]:
    """Detect fenced code blocks and common unfenced code patterns."""
    blocks = extract_code_blocks(text)
    remaining_text = re.sub(
        r"```[^\n`]*\n.*?```",
        "",
        text or "",
        flags=re.DOTALL,
    )

    # Detect common code patterns outside fenced Markdown blocks.
    if remaining_text.strip():
        detection = detect_language(remaining_text)

        if detection["language"] != "Unknown":
            blocks.append({
                "code": remaining_text.strip(),
                "declared_language": "Not specified",
                "detected_language": detection["language"],
                "confidence": detection["confidence"],
                "format": "unfenced",
            })

    for block in blocks:
        block.setdefault("format", "fenced")

    return {
        "contains_code": bool(blocks),
        "code_block_count": len(blocks),
        "code_blocks": blocks,
    }
