"""Categorize a document using its filename (and a bit of its text)."""
import os

CATEGORY_KEYWORDS = {
    "Questions": ["question", "qb", "qp", "paper", "pyq", "exam", "quiz",
                  "mcq", "assignment", "worksheet", "bank"],
    "Labs": ["lab", "practical", "experiment", "manual"],
    "Notes": ["note", "notes", "lecture", "slides", "ppt", "summary", "unit", "module"],
    "Textbook": ["textbook", "book", "chapter", "edition", "reference", "ebook"],
}
# Order matters: first match wins
PRIORITY = ["Questions", "Labs", "Textbook", "Notes"]


def categorize(filename: str, text: str = "") -> str:
    name = os.path.splitext(os.path.basename(filename))[0].lower()
    name = name.replace("_", " ").replace("-", " ")
    for cat in PRIORITY:
        if any(k in name.split() or k in name for k in CATEGORY_KEYWORDS[cat]):
            return cat
    # Fallback: peek at first part of the text
    head = (text or "")[:1500].lower()
    if head.count("q.") + head.count("question") >= 3:
        return "Questions"
    if "experiment" in head or "aim:" in head:
        return "Labs"
    return "Other"
