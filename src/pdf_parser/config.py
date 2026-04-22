"""Configuration models for the PDF parsing pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    """Runtime configuration for the PDF parsing application."""

    input_dir: Path = Path("./pdfs")
    output_dir: Path = Path("./output")
    archive_name: str = "submission"
    pdf_pattern: str = "document_*.pdf"
    marker_command: str = "marker_single"
    marker_output_format: str = "markdown"
    marker_timeout_sec: int = 300
    do_ocr: bool = True
    generate_picture_images: bool = True
    fail_fast: bool = False
    keep_temporary_dirs: bool = False
    image_dir_name: str = "_image"
    log_level: str = "INFO"
    supported_suffixes: tuple[str, ...] = field(default_factory=lambda: (".pdf",))

    @property
    def image_dir(self) -> Path:
        """Return the directory used for extracted images."""
        return self.output_dir / self.image_dir_name
