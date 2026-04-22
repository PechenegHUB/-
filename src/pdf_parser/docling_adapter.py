"""Docling integration for tables and images extraction."""

from __future__ import annotations

from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    TableFormerMode,
    TableStructureOptions,
    ThreadedPdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import PictureItem, TableItem, TextItem

from pdf_parser.config import AppConfig
from pdf_parser.exceptions import ConversionError
from pdf_parser.markdown import ImageReference, is_caption, safe_table_to_markdown


class DoclingExtractor:
    """Extract tables and caption-linked images from PDFs using Docling."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF],
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=ThreadedPdfPipelineOptions(
                        do_ocr=config.do_ocr,
                        generate_picture_images=config.generate_picture_images,
                        table_structure_options=TableStructureOptions(mode=TableFormerMode.ACCURATE),
                    )
                )
            },
        )

    def extract(self, pdf_path: Path, image_dir: Path, doc_number: str) -> tuple[list[str], list[ImageReference]]:
        """Extract tables and figure images from a PDF."""
        try:
            result = self._converter.convert(pdf_path)
        except Exception as exc:  # pragma: no cover
            raise ConversionError(f"Docling failed for '{pdf_path.name}': {exc}") from exc

        tables: list[str] = []
        images: list[ImageReference] = []
        image_index = 1
        last_picture: PictureItem | None = None

        for element, _ in result.document.iterate_items():
            if isinstance(element, TableItem):
                try:
                    table_md = safe_table_to_markdown(element)
                except Exception as exc:
                    raise ConversionError(
                        f"Failed to convert a table in '{pdf_path.name}' to Markdown: {exc}"
                    ) from exc
                if table_md:
                    tables.append(table_md)
                continue

            if isinstance(element, PictureItem):
                last_picture = element
                continue

            if isinstance(element, TextItem) and last_picture is not None:
                caption = element.text.strip()
                if is_caption(caption) and last_picture.image is not None:
                    image_name = f"doc_{doc_number}_image_{image_index}.png"
                    output_path = image_dir / image_name
                    last_picture.image.pil_image.save(output_path, "PNG")
                    images.append(ImageReference(relative_path=f"{image_dir.name}/{image_name}", caption=caption))
                    image_index += 1
                last_picture = None

        return tables, images
