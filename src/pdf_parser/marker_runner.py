"""Integration with Marker CLI."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from pdf_parser.config import AppConfig
from pdf_parser.exceptions import MarkerExecutionError, MarkerOutputNotFoundError


class MarkerRunner:
    """Wrapper around Marker CLI invocation."""

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def ensure_available(self) -> None:
        """Validate that Marker CLI is available in the environment."""
        if shutil.which(self._config.marker_command) is None:
            raise FileNotFoundError(
                f"Marker executable '{self._config.marker_command}' was not found in PATH."
            )

    def run(self, pdf_path: Path, temp_dir: Path) -> Path:
        """Run Marker for a single PDF file."""
        command = [
            self._config.marker_command,
            str(pdf_path),
            "--output_dir",
            str(temp_dir),
            "--output_format",
            self._config.marker_output_format,
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=self._config.marker_timeout_sec,
        )
        if result.returncode != 0:
            raise MarkerExecutionError(
                f"Marker failed for '{pdf_path.name}' with code {result.returncode}.\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

        markdown_path = next(temp_dir.rglob("*.md"), None)
        if markdown_path is None:
            raise MarkerOutputNotFoundError(
                f"Marker finished for '{pdf_path.name}' but no Markdown file was found."
            )
        return markdown_path
