"""HTML→PDF 변환 유틸리티 (WeasyPrint 사용, graceful fail)."""
from __future__ import annotations

from pathlib import Path


def generate_pdf(html: str, output_path: str) -> bool:
    """Generate a PDF from HTML string.

    Args:
        html: HTML content to convert.
        output_path: Destination PDF path.
    Returns:
        True if PDF generated, False if fallback HTML created due to missing dependency.
    """
    try:
        from weasyprint import HTML  # type: ignore
    except Exception:
        Path(output_path).with_suffix(".html").write_text(html, encoding="utf-8")
        return False

    HTML(string=html).write_pdf(output_path)
    return True
