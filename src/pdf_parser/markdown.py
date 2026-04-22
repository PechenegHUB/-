"""Markdown helpers for converting tables and inserting images."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from pdf_parser.cleaning import strip_html

CAPTION_ANCHOR_RE = re.compile(r"^(Рис\.|Рисунок|Фиг\.|Fig\.|Figure)\s*", flags=re.IGNORECASE)


@dataclass(slots=True, frozen=True)
class ImageReference:
    """Information required to insert an image into Markdown."""

    relative_path: str
    caption: str


def is_caption(text: str) -> bool:
    """Check whether a text line looks like a figure caption."""
    return bool(CAPTION_ANCHOR_RE.match(text.strip()))


def safe_table_to_markdown(table_item: Any) -> str:
    """Convert a Docling table item into GitHub-flavored Markdown."""
    data = table_item.data
    if not data.table_cells:
        return ""

    max_r = max((cell.end_row_offset_idx for cell in data.table_cells), default=0)
    max_c = max((cell.end_col_offset_idx for cell in data.table_cells), default=0)
    num_rows = max(data.num_rows, max_r)
    num_cols = max(data.num_cols, max_c)

    if num_rows <= 0 or num_cols <= 0:
        raise ValueError("Table dimensions must be positive.")

    grid = [["" for _ in range(num_cols)] for _ in range(num_rows)]

    for cell in data.table_cells:
        cell_text = strip_html(cell.text or "").strip().replace("\n", " ").replace("|", r"\|")
        for row_idx in range(cell.start_row_offset_idx, min(cell.end_row_offset_idx, num_rows)):
            for col_idx in range(cell.start_col_offset_idx, min(cell.end_col_offset_idx, num_cols)):
                if not grid[row_idx][col_idx]:
                    grid[row_idx][col_idx] = cell_text

    header = "| " + " | ".join(grid[0]) + " |"
    separator = "| " + " | ".join(["---"] * num_cols) + " |"
    body = ["| " + " | ".join(row) + " |" for row in grid[1:]]
    return "\n".join([header, separator, *body])


def insert_images_into_markdown(content: str, images: list[ImageReference]) -> str:
    """Insert Markdown image tags above matching captions."""
    updated = content
    for image in images:
        updated = re.sub(
            rf"({re.escape(image.caption)})",
            rf"![image]({image.relative_path})\n\n\1",
            updated,
            count=1,
        )
    return updated
