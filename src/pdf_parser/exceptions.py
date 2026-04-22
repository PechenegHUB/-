"""Custom exceptions used across the PDF parsing pipeline."""


class PdfParserError(Exception):
    """Base exception for project-specific errors."""


class MarkerExecutionError(PdfParserError):
    """Raised when the Marker CLI fails to process a PDF file."""


class MarkerOutputNotFoundError(PdfParserError):
    """Raised when Marker finishes without producing a Markdown file."""


class ConversionError(PdfParserError):
    """Raised when a document conversion step cannot be completed."""
