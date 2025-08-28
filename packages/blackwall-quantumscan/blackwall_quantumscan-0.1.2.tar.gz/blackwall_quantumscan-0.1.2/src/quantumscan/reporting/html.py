"""Jinja2 HTML report renderer."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Sequence

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

TEMPLATE_NAME = "report.html.j2"


def render_html_report(
    findings: List[Dict[str, Any]],
    summary: Dict[str, int],
    mapping: Dict[str, List[str]],
    *,
    references: Sequence[str] | None = None,
    outfile: str | None = None,
) -> str:
    """Render findings into an HTML report.

    Args:
        findings: List of finding dicts.
        summary: Summary statistics.
        mapping: Algorithm replacement mapping.
        outfile: Optional path to write the HTML file.
    Returns:
        Rendered HTML string.
    """
    template_dir = Path(__file__).with_name("templates")
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "j2"]),
        undefined=StrictUndefined,
    )

    risk_counts = Counter({"critical": 0, "high": 0, "medium": 0, "low": 0, "none": 0})
    for item in findings:
        risk_counts[item.get("risk", "none")] += 1

    template = env.get_template(TEMPLATE_NAME)
    html = template.render(
        findings=findings,
        summary=summary,
        mapping=mapping,
        risk_counts=risk_counts,
        references=references or [],
    )

    if outfile:
        Path(outfile).write_text(html, encoding="utf-8")
    return html
