"""Text cleaning utilities used after Marker Markdown extraction."""

from __future__ import annotations

import re

HTML_TAGS_RE = re.compile(r"<[^>]+>")
HTML_TABLE_RE = re.compile(r"<table\b.*?</table>", flags=re.IGNORECASE | re.DOTALL)
PAGE_MARKER_RE = re.compile(r"\{?\d+\}?-{5,}.*")
JUNK_PHRASES_RE = re.compile(
    r"\b(Huff LLC|the state|draft|черновик|study|изучить)\b.*?\d{4}-\d{2}-\d{2}|"
    r"Huff LLC|"
    r"^\s*[-–—]?\s*\d+\s*(?:/\s*\d+)?\s*[-–—]?\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)
REPETITION_RE = re.compile(r"\b(?P<word>\w+)\b(?:\s+(?P=word)\b){2,}", flags=re.IGNORECASE)
NOISE_LINE_RE = re.compile(r"^[_\s\d\-\|\\/]+$")


def strip_html(text: str) -> str:
    """Remove HTML tables and tags from text."""
    text = HTML_TABLE_RE.sub("", text)
    return HTML_TAGS_RE.sub("", text)


def deep_clean(text: str) -> str:
    """Perform multi-step cleanup of Markdown content."""
    text = strip_html(text)
    text = JUNK_PHRASES_RE.sub("", text)
    text = REPETITION_RE.sub(lambda match: match.group("word"), text)
    text = PAGE_MARKER_RE.sub("", text)

    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if NOISE_LINE_RE.match(stripped):
            continue
        lines.append(line)

    return "\n".join(lines).strip()
