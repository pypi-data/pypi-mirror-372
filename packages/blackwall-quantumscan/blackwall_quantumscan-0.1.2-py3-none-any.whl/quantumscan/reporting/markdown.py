"""Markdown report generation for QuantumScan results."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping

from .pqc_mapping import NIST_URLS, get_pqc_replacement

SEVERITY_MAP = {"RSA": "High", "ECC": "High", "SHA-1": "Medium", "MD5": "Medium"}


def _escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("*", "\\*")
        .replace("_", "\\_")
        .replace("`", "\\`")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _shorten(text: str, limit: int = 120) -> str:
    if len(text) <= limit:
        return text
    head = limit // 2
    tail = limit - head - 1
    return text[:head] + "…" + text[-tail:]


def generate_markdown_report(
    data: Mapping[str, Any], *, output_path: str | Path | None = None, metadata: Mapping[str, Any] | None = None
) -> str:
    """Generate a markdown report from scan results."""
    if "findings" not in data:
        raise ValueError("findings key required")

    findings: Iterable[Mapping[str, Any]] = data.get("findings", [])
    errors: Iterable[Mapping[str, Any]] = data.get("errors", [])
    metadata = metadata or {}

    lines: list[str] = ["# QuantumScan Report (Markdown)", ""]

    file_count = len({f["path"] for f in findings})
    summary = ["**Summary**", f"Total Files: {file_count}", f"Total Findings: {len(list(findings))}", f"Errors: {len(list(errors))}"]

    version = metadata.get("version")
    if version:
        summary.append(f"Version: {version}")

    try:
        started = datetime.fromisoformat(metadata.get("started_at", ""))
        ended = datetime.fromisoformat(metadata.get("ended_at", ""))
        runtime = (ended - started).total_seconds()
        if runtime:
            summary.append(f"Runtime (s): {runtime:.2f}")
    except Exception:
        pass

    lines.extend(summary)
    lines.append("")

    findings = list(findings)
    pqc_rows: list[str] = []
    seen_algos: set[str] = set()
    if findings:
        table = ["| Path | Line | Algorithm | Evidence | Severity |", "| --- | --- | --- | --- | --- |"]
        for f in findings:
            ev = _escape(_shorten(str(f.get("evidence", ""))))
            algo = f.get("algo")
            sev = SEVERITY_MAP.get(algo, "Info")
            table.append(f"| {f.get('path')} | {f.get('line')} | {algo} | {ev} | {sev} |")

            if algo not in seen_algos:
                seen_algos.add(algo)
                mapping = get_pqc_replacement(algo)
                rec_names = ", ".join(
                    f"{r['name']} ({r.get('short')})" if r.get("short") else r["name"]
                    for r in mapping["recommended"]
                )
                links = ", ".join(
                    f"[{r.get('short', r['name'])}]({r['nist_ref']})" for r in mapping["recommended"]
                )
                if not rec_names:
                    rec_names = "대체 없음"
                    links = ""
                risk = SEVERITY_MAP.get(algo, "Info")
                pqc_rows.append(f"| {algo} | {rec_names} | {links} | {risk} |")
        lines.extend(table)
    else:
        lines.append("No findings")

    lines.append("")
    lines.append("## PQC 교체 가이드")
    if pqc_rows:
        guide = ["| 취약 알고리즘 | 권고 PQC(알고리즘/모드) | 근거(NIST 등 링크) | 리스크 등급 |", "| --- | --- | --- | --- |"]
        guide.extend(pqc_rows)
        lines.extend(guide)
    else:
        lines.append("탐지된 취약 알고리즘 없음")

    errors = list(errors)
    if errors:
        lines.append("")
        lines.append("**Errors**")
        table = ["| Path | Error |", "| --- | --- |"]
        for e in errors:
            table.append(f"| {_escape(str(e.get('path')))} | {_escape(str(e.get('error')))} |")
        lines.extend(table)

    if metadata:
        lines.append("")
        lines.append("**Metadata**")
        lines.append("```json")
        lines.append(json.dumps(metadata, indent=2))
        lines.append("```")

    lines.append("")
    lines.append("## NIST References")
    lines.extend(
        [
            f"- [FIPS 203 — ML-KEM (CRYSTALS-Kyber)]({NIST_URLS['FIPS_203']})",
            f"- [FIPS 204 — ML-DSA (CRYSTALS-Dilithium)]({NIST_URLS['FIPS_204']})",
            f"- [FIPS 205 — SLH-DSA (SPHINCS+)]({NIST_URLS['FIPS_205']})",
            f"- [NIST PQC Selected Algorithms]({NIST_URLS['SELECTED_ALGOS']})",
            f"- [NIST News (FIPS 승인 공지)]({NIST_URLS['FIPS_NEWS']})",
        ]
    )

    text = "\n".join(lines) + "\n"

    if output_path is not None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(f".{out.name}.tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(str(tmp), str(out))
    return text
