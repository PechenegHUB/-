"""End-to-end PDF processing pipeline."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from pdf_parser.cleaning import deep_clean
from pdf_parser.config import AppConfig
from pdf_parser.docling_adapter import DoclingExtractor
from pdf_parser.logging_utils import get_logger
from pdf_parser.markdown import insert_images_into_markdown
from pdf_parser.marker_runner import MarkerRunner

LOGGER = get_logger("pipeline")
DOC_NUMBER_RE = re.compile(r"(\d+)$")


@dataclass(slots=True, frozen=True)
class FileProcessingResult:
    """Summary of processing outcome for a single PDF."""

    pdf_name: str
    markdown_path: Path | None
    success: bool
    error: str | None = None


class PdfProcessingPipeline:
    """Coordinate Marker, Docling and output assembly for many PDFs."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._marker = MarkerRunner(config)
        self._docling = DoclingExtractor(config)

    def run(self) -> list[FileProcessingResult]:
        """Process all configured PDF files."""
        self._validate_inputs()
        self._marker.ensure_available()
        self._prepare_output_dirs()

        pdf_files = sorted(self._config.input_dir.glob(self._config.pdf_pattern))
        results: list[FileProcessingResult] = []

        LOGGER.info("Found %d PDF files matching pattern '%s'.", len(pdf_files), self._config.pdf_pattern)

        for pdf_path in pdf_files:
            result = self._process_single(pdf_path)
            results.append(result)
            if not result.success and self._config.fail_fast:
                break

        self._make_archive()
        return results

    def _validate_inputs(self) -> None:
        if not self._config.input_dir.exists():
            raise FileNotFoundError(f"Input directory does not exist: {self._config.input_dir}")
        if not self._config.input_dir.is_dir():
            raise NotADirectoryError(f"Input path is not a directory: {self._config.input_dir}")

    def _prepare_output_dirs(self) -> None:
        self._config.output_dir.mkdir(parents=True, exist_ok=True)
        self._config.image_dir.mkdir(parents=True, exist_ok=True)

    def _process_single(self, pdf_path: Path) -> FileProcessingResult:
        stem = pdf_path.stem
        doc_number = self._extract_document_number(stem)
        temp_dir = self._config.output_dir / f"_tmp_{stem}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        try:
            LOGGER.info("Processing '%s'.", pdf_path.name)
            marker_md_path = self._marker.run(pdf_path, temp_dir)
            content = deep_clean(marker_md_path.read_text(encoding="utf-8"))
            tables, images = self._docling.extract(pdf_path, self._config.image_dir, doc_number)
            content = insert_images_into_markdown(content, images)
            if tables:
                content = content + "\n\n" + "\n\n".join(tables)

            output_md_path = self._config.output_dir / f"{stem}.md"
            output_md_path.write_text(content, encoding="utf-8")
            LOGGER.info("Saved '%s'.", output_md_path.name)
            return FileProcessingResult(pdf_name=pdf_path.name, markdown_path=output_md_path, success=True)
        except Exception as exc:
            LOGGER.exception("Failed to process '%s'.", pdf_path.name)
            return FileProcessingResult(
                pdf_name=pdf_path.name,
                markdown_path=None,
                success=False,
                error=str(exc),
            )
        finally:
            if not self._config.keep_temporary_dirs and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _make_archive(self) -> Path:
        archive_path = shutil.make_archive(
            base_name=self._config.archive_name,
            format="zip",
            root_dir=self._config.output_dir,
        )
        LOGGER.info("Created archive '%s'.", archive_path)
        return Path(archive_path)

    @staticmethod
    def _extract_document_number(stem: str) -> str:
        match = DOC_NUMBER_RE.search(stem)
        return match.group(1) if match else "0"
