"""Text cleaning: extra spaces, blank lines, symbols, repeated text."""
import re


def clean_text(text: str) -> str:
    if not text:
        return ""
    # Remove weird/invisible characters
    text = text.replace("\x00", " ").replace("\u200b", "").replace("\xa0", " ")
    # Remove unnecessary symbols (keep letters, numbers, common punctuation)
    text = re.sub(r"[^\w\s.,;:!?()\[\]{}'\"%+\-*/=<>@&$\u0900-\u097F]", " ", text)
    # Remove extra spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip() for line in text.splitlines()]
    # Remove blank lines + repeated consecutive lines
    cleaned, prev = [], None
    for line in lines:
        if not line or line == prev:
            continue
        cleaned.append(line)
        prev = line
    return "\n".join(cleaned).strip()


def remove_repeated_lines(pages: list) -> list:
    """Remove headers/footers that repeat on many pages.
    pages: list of dicts with a 'text' key. Returns the same list, cleaned."""
    if len(pages) < 3:
        return pages
    counts = {}
    for p in pages:
        for line in set(p["text"].splitlines()):
            counts[line] = counts.get(line, 0) + 1
    limit = max(3, int(len(pages) * 0.6))
    repeated = {l for l, c in counts.items() if c >= limit and len(l) < 80}
    for p in pages:
        p["text"] = "\n".join(l for l in p["text"].splitlines() if l not in repeated)
    return pages
