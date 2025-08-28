"""QuantumScan CLI providing simple vulnerable algorithm scanning."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable
from datetime import datetime

from quantumscan import __version__
from quantumscan.parser.models import ErrorCode, Finding
from quantumscan.parser.scanner import scan
from quantumscan.reporting.html import render_html_report
from quantumscan.reporting.pdf import generate_pdf
from quantumscan.reporting.pqc_mapping import NIST_URLS, get_pqc_replacement

ALGO_MAP = {
    "rsa": "RSA",
    "ecc": "ECC",
    "ec": "ECC",
    "secp256k1": "ECC",
    "md5": "MD5",
    "sha1": "SHA-1",
}


def _str2bool(val: str) -> bool:
    true_set = {"1", "true", "yes", "y", "on"}
    false_set = {"0", "false", "no", "n", "off"}
    lowered = val.lower()
    if lowered in true_set:
        return True
    if lowered in false_set:
        return False
    raise argparse.ArgumentTypeError("Boolean value expected.")


def _rel(path: str) -> str:
    p = Path(path).resolve()
    try:
        return str(p.relative_to(Path.cwd()))
    except ValueError:  # outside cwd
        return str(p)


def _format_evidence(text: str, max_len: int) -> str:
    norm = " ".join(text.split())
    if len(norm) > max_len:
        return norm[: max_len - 3] + "..."
    return norm


def _emit(findings: Iterable[Finding], *, algos: set[str] | None, max_len: int) -> None:
    for f in findings:
        if algos and f.algorithm not in algos:
            continue
        evidence = _format_evidence(f.evidence, max_len)
        print(f"{_rel(f.path)}:{f.lineno}: {f.algorithm} | token='{evidence}'")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="quantumscan")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument("--path", default=".", help="Path to scan")
    parser.add_argument(
        "--algo",
        help="Comma-separated algorithms to include (rsa,ecc,md5,sha1)",
    )
    parser.add_argument(
        "--max-evidence-len",
        type=int,
        default=120,
        dest="max_evidence_len",
        help="Maximum length of evidence token",
    )
    parser.add_argument(
        "--max-file-mb",
        type=int,
        default=5,
        dest="max_file_mb",
        help="Maximum file size to scan in megabytes",
    )
    parser.add_argument(
        "--report",
        help="Report format (markdown) or path to save HTML/PDF output",
    )
    parser.add_argument(
        "--output",
        help="Path to save report output when --report is a format",
    )
    parser.add_argument(
        "--format",
        choices=["html", "pdf"],
        default="html",
        help="Report format when --report is a path",
    )
    parser.add_argument(
        "--fail-on-findings",
        type=_str2bool,
        default=False,
        help="Exit with code 1 if findings are detected (true/false)",
    )
    parser.add_argument(
        "--exclude",
        help="Comma-separated paths to exclude from scanning",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(f"quantumscan v{__version__}")
        return 0

    target = Path(args.path)
    if not target.exists():
        print(f"error: path not found: {args.path}", file=sys.stderr)
        return 2

    algos = None
    if args.algo:
        algos = {ALGO_MAP[a.strip().lower()] for a in args.algo.split(",") if a.strip().lower() in ALGO_MAP}

    start_ts = datetime.utcnow()
    max_bytes = args.max_file_mb * 1024 * 1024
    exclude = [e.strip() for e in args.exclude.split(",") if e.strip()] if args.exclude else None

    records, findings, stats = scan(
        [str(target)],
        extensions=[".py", ".js", ".java", ".c", ".cpp", ".go"],
        max_size=max_bytes,
        exclude=exclude,
    )

    for r in records:
        if r.error_code == ErrorCode.DECODE_ERROR:
            print(f"WARN decode {_rel(r.path)}", file=sys.stderr)
        elif r.error_code == ErrorCode.TOO_LARGE:
            print(
                f"WARN SKIPPED_LARGE_FILE {_rel(r.path)} size>{max_bytes}",
                file=sys.stderr,
            )
        elif r.error_code == ErrorCode.SYMLINK_LOOP:
            print(f"WARN SYMLINK_LOOP_DETECTED {_rel(r.path)}", file=sys.stderr)

    _emit(findings, algos=algos, max_len=args.max_evidence_len)
    filtered = [f for f in findings if not algos or f.algorithm in algos]

    if args.report:
        if args.report == "markdown":
            if not args.output:
                print("error: --output required when --report markdown", file=sys.stderr)
                return 2
            out = Path(args.output)
            try:
                out.parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(f"error: {e}", file=sys.stderr)
                return 2
            with out.open("w", encoding="utf-8") as fh:
                fh.write("# QuantumScan Report\n\n")
                for f in filtered:
                    evidence = _format_evidence(f.evidence, args.max_evidence_len)
                    fh.write(
                        f"- {_rel(f.path)}:{f.lineno}: {f.algorithm} | token='{evidence}'\n"
                    )
            print(f"Saved Markdown report to: {out.resolve()}")
        else:
            fmt = args.format
            out = Path(args.report)
            try:
                out.parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(f"error: {e}", file=sys.stderr)
                return 2

            summary = {
                "scanned": stats["files"],
                "skipped": stats["skipped"]
                + stats["skipped_large"]
                + stats["skipped_symlink_loop"],
                "errors": stats["errors"],
            }
            findings_data = [
                {
                    "path": _rel(f.path),
                    "line": f.lineno,
                    "algorithm": f.algorithm,
                    "evidence": f.evidence,
                    "risk": "high",
                }
                for f in filtered
            ]
            mapping: dict[str, list[str]] = {}
            refs: set[str] = set(NIST_URLS.values())
            for algo in {f.algorithm for f in filtered}:
                rep = get_pqc_replacement(algo)
                mapping[algo] = [r["name"] for r in rep["recommended"]]
                refs.update(rep["links"])

            if fmt == "html":
                try:
                    render_html_report(
                        findings_data,
                        summary,
                        mapping,
                        references=sorted(refs),
                        outfile=str(out),
                    )
                except OSError as e:
                    print(f"error: {e}", file=sys.stderr)
                    return 2
                print(f"Saved HTML report to: {out.resolve()}")
            elif fmt == "pdf":
                html = render_html_report(
                    findings_data, summary, mapping, references=sorted(refs)
                )
                success = generate_pdf(html, str(out))
                if success:
                    print(f"Saved PDF report to: {out.resolve()}")
                else:
                    backup = out.with_suffix(".html")
                    print(
                        f"WARN weasyprint missing; saved HTML to: {backup.resolve()}",
                        file=sys.stderr,
                    )
            else:  # pragma: no cover - argparse enforces
                print(f"error: unknown format {fmt}", file=sys.stderr)
                return 2
    if args.fail_on_findings and filtered:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())

