"""Utilities to render QuantumScan CI summary comments."""
from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable

ANCHOR = "<!-- QUANTUMSCAN_PR_SUMMARY -->"


def _normalize_detection(item: Dict) -> Dict | None:
    try:
        path = str(item["path"])
        line = int(item["line"])
        algo = str(item["algorithm"])
    except Exception:
        return None
    return {"path": path, "line": line, "algorithm": algo}


def render_summary(data: Dict) -> str:
    """Render a markdown summary for PR comments.

    Parameters
    ----------
    data:
        Dictionary containing keys ``sha``, ``total_files`` and ``detections``.
    """
    required = {"sha", "total_files", "detections"}
    if not required <= data.keys():
        missing = ", ".join(sorted(required - data.keys()))
        raise ValueError(f"missing keys: {missing}")

    sha = str(data["sha"])
    total_files = int(data["total_files"])
    detections = [_normalize_detection(d) for d in data.get("detections", [])]
    detections = [d for d in detections if d is not None]

    if not detections:
        return (
            f"{ANCHOR}\n"
            "### QuantumScan Summary\n"
            f"- Commit: `{sha}`\n"
            f"- 총 {total_files}개 파일 검사\n"
            "🟢 문제 없음"
        )

    counts = Counter(d["algorithm"] for d in detections)
    summary = ", ".join(f"{k}:{v}" for k, v in counts.items())
    top = detections[:5]
    top_lines = "\n".join(f"- {d['path']}:{d['line']} | {d['algorithm']}" for d in top)
    more = "\n...and more" if len(detections) > 5 else ""

    body = (
        f"{ANCHOR}\n"
        "### QuantumScan Summary\n"
        f"- Commit: `{sha}`\n"
        f"- 총 {total_files}개 파일 검사\n"
        f"- 탐지 요약: {summary}\n"
        "#### Top 5\n"
        f"{top_lines}{more}"
    )

    lines = body.splitlines()[:1000]
    return "\n".join(lines)
