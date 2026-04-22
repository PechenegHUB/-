"""Command-line interface for the PDF parsing pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from pdf_parser.config import AppConfig
from pdf_parser.logging_utils import configure_logging, get_logger
from pdf_parser.pipeline import PdfProcessingPipeline

LOGGER = get_logger("cli")


def build_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Convert PDFs into cleaned Markdown.")
    parser.add_argument("--input-dir", type=Path, default=Path("./pdfs"), help="Directory with input PDF files.")
    parser.add_argument("--output-dir", type=Path, default=Path("./output"), help="Directory for generated Markdown files.")
    parser.add_argument("--archive-name", type=str, default="submission", help="Result ZIP archive name without extension.")
    parser.add_argument("--pdf-pattern", type=str, default="document_*.pdf", help="Glob pattern for selecting PDF files.")
    parser.add_argument("--marker-command", type=str, default="marker_single", help="Marker CLI executable.")
    parser.add_argument("--marker-timeout-sec", type=int, default=300, help="Timeout for one Marker run.")
    parser.add_argument("--no-ocr", action="store_true", help="Disable OCR in Docling.")
    parser.add_argument("--keep-temporary-dirs", action="store_true", help="Preserve intermediate Marker directories for debugging.")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on the first processing error.")
    parser.add_argument("--log-level", type=str, default="INFO", help="Logging level, for example INFO or DEBUG.")
    return parser


def main() -> int:
    """CLI entry point."""
    args = build_parser().parse_args()
    configure_logging(args.log_level)

    config = AppConfig(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        archive_name=args.archive_name,
        pdf_pattern=args.pdf_pattern,
        marker_command=args.marker_command,
        marker_timeout_sec=args.marker_timeout_sec,
        do_ocr=not args.no_ocr,
        keep_temporary_dirs=args.keep_temporary_dirs,
        fail_fast=args.fail_fast,
        log_level=args.log_level,
    )

    pipeline = PdfProcessingPipeline(config)
    results = pipeline.run()

    success_count = sum(result.success for result in results)
    failure_count = len(results) - success_count
    LOGGER.info("Completed. Success: %d, failed: %d.", success_count, failure_count)
    return 0 if failure_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
