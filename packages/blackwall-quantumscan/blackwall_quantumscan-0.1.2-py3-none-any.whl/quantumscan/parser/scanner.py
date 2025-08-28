from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

from .models import FileRecord, ErrorCode, Finding, Severity
from .utils import (
    detect_language,
    read_text_safely,
    sha256sum,
    is_supported_ext,
    should_skip_dir,
    EXCLUDE_DIRS,
    MAX_SIZE,
)

REGEXES: Dict[str, List[re.Pattern[str]]] = {
    "RSA": [
        re.compile(r"BEGIN RSA (?:PUBLIC|PRIVATE) KEY", re.I),
        re.compile(r"RSA_(?:PUBLIC|PRIVATE)_KEY", re.I),
        re.compile(r"cryptography\.hazmat\.[\w\.]*RSA(?:Private|Public)Key", re.I),
        re.compile(r"rsa\.(?:new|generate|encrypt|decrypt)", re.I),
        re.compile(r'KeyPairGenerator\.getInstance\(["\']RSA["\']\)', re.I),
        re.compile(r'Cipher\.getInstance\(["\']RSA(?:/[^"\']+)?["\']\)', re.I),
        re.compile(r"crypto\.publicEncrypt|crypto\.privateDecrypt", re.I),
        re.compile(r"create(?:Public|Private)Key\(", re.I),
        re.compile(r"EVP_PKEY_RSA", re.I),
        re.compile(r"RSA_\w*\(", re.I),
        re.compile(r"OPENSSL_.*RSA", re.I),
        re.compile(r"rsa\.\w+", re.I),
    ],
    "ECC": [
        re.compile(r"\bEC(?:D[SAH])?\b", re.I),
        re.compile(r"\bsecp\d{3}[kpr]?1\b", re.I),
        re.compile(r"\bP-?(?:256|384|521)\b", re.I),
        re.compile(r"Elliptic\s*Curve", re.I),
        re.compile(r'KeyPairGenerator\.getInstance\(["\']EC["\']\)', re.I),
        re.compile(r"createECDH\(|ECDH\(", re.I),
        re.compile(r"EC_KEY_\w+", re.I),
        re.compile(r"EVP_PKEY_EC", re.I),
        re.compile(r"elliptic\.(?:P256|P384|P521)", re.I),
    ],
    "SHA-1": [
        re.compile(r"\bSHA-?1\b", re.I),
        re.compile(r"hashlib\.sha1\(", re.I),
        re.compile(r'MessageDigest\.getInstance\(["\']SHA-?1["\']\)', re.I),
        re.compile(r'crypto\.createHash\(["\']sha1["\']\)', re.I),
        re.compile(r"EVP_sha1\(", re.I),
    ],
    "MD5": [
        re.compile(r"\bMD5\b", re.I),
        re.compile(r"hashlib\.md5\(", re.I),
        re.compile(r'MessageDigest\.getInstance\(["\']MD5["\']\)', re.I),
        re.compile(r'crypto\.createHash\(["\']md5["\']\)', re.I),
        re.compile(r"EVP_md5\(", re.I),
    ],
}


def scan(
    paths: Iterable[str],
    *,
    follow_symlinks: bool = False,
    max_size: int = MAX_SIZE,
    extensions: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
) -> tuple[List[FileRecord], List[Finding], Dict[str, int]]:
    records: List[FileRecord] = []
    findings: List[Finding] = []
    stats: Dict[str, int] = {
        "files": 0,
        "skipped": 0,
        "errors": 0,
        "skipped_large": 0,
        "skipped_symlink_loop": 0,
    }
    visited_dirs: Set[Tuple[int, int]] = set()
    excluded = {Path(e).resolve() for e in (exclude or [])}

    def is_excluded(p: Path) -> bool:
        rp = p.resolve()
        return any(ex == rp or ex in rp.parents for ex in excluded)

    def walk(p: Path):
        try:
            if is_excluded(p):
                return
            if p.is_dir():
                if should_skip_dir(p.name):
                    return
                if p.is_symlink() and not follow_symlinks:
                    return
                try:
                    stat = p.stat(follow_symlinks=follow_symlinks)
                except OSError as e:  # pragma: no cover - rare filesystem error
                    records.append(_error_record(p, ErrorCode.IO_ERROR, str(e)))
                    return
                key = (stat.st_dev, stat.st_ino)
                if key in visited_dirs:
                    stats["skipped_symlink_loop"] += 1
                    records.append(_error_record(p, ErrorCode.SYMLINK_LOOP))
                    return
                visited_dirs.add(key)
                for child in p.iterdir():
                    walk(child)
            elif p.is_file():
                process_file(p)
            else:
                return  # pragma: no cover - non-regular paths
        except OSError as e:  # pragma: no cover - path access race
            records.append(_error_record(p, ErrorCode.IO_ERROR, str(e)))

    def process_file(p: Path):
        ext = p.suffix.lower()
        stats["files"] += 1
        try:
            stat = p.stat()
            size = stat.st_size
            modified = stat.st_mtime
        except OSError as e:  # pragma: no cover - inaccessible file
            stats["errors"] += 1
            records.append(FileRecord(
                path=str(p),
                ext=ext,
                language=detect_language(ext),
                size=0,
                sha256="",
                line_count=0,
                modified_ts=0.0,
                content=None,
                error_code=ErrorCode.IO_ERROR,
                error_detail=str(e),
            ))
            return
        if size > max_size:
            sha = sha256sum(p)
            stats["errors"] += 1
            stats["skipped_large"] += 1
            records.append(FileRecord(
                path=str(p),
                ext=ext,
                language=detect_language(ext),
                size=size,
                sha256=sha,
                line_count=0,
                modified_ts=modified,
                content=None,
                error_code=ErrorCode.TOO_LARGE,
            ))
            return
        if not is_supported_ext(ext, extensions):
            stats["skipped"] += 1
            return
        language = detect_language(ext)
        sha = sha256sum(p)
        text, err = read_text_safely(p)
        line_count = text.count("\n") + (1 if text and not text.endswith("\n") else 0) if text is not None else 0
        record = FileRecord(
            path=str(p),
            ext=ext,
            language=language,
            size=size,
            sha256=sha,
            line_count=line_count,
            modified_ts=modified,
            content=text,
            error_code=err,
        )
        records.append(record)
        if err is not None:
            stats["errors"] += 1
            return
        findings.extend(_detect_findings(record))

    def _error_record(p: Path, code: ErrorCode, detail: str | None = None) -> FileRecord:
        stats["errors"] += 1
        return FileRecord(
            path=str(p),
            ext=p.suffix.lower(),
            language=detect_language(p.suffix.lower()),
            size=0,
            sha256="",
            line_count=0,
            modified_ts=0.0,
            content=None,
            error_code=code,
            error_detail=detail,
        )

    for path in paths:
        walk(Path(path))

    records.sort(key=lambda r: r.path)
    return records, findings, stats


def _detect_findings(record: FileRecord) -> List[Finding]:
    """Regex scan that captures raw evidence tokens for CLI output."""
    if not record.content:
        return []
    findings: List[Finding] = []
    lines = record.content.splitlines()
    for lineno, line in enumerate(lines, start=1):
        best: Dict[str, tuple[str, int]] = {}
        for algo, patterns in REGEXES.items():
            for pat in patterns:
                for match in pat.finditer(line):
                    token = match.group(0)
                    cur = best.get(algo)
                    if not cur or len(token) > len(cur[0]):
                        best[algo] = (token, match.start())
        for algo, (token, col) in best.items():
            severity = Severity.HIGH if algo in {"SHA-1", "MD5"} else Severity.MEDIUM
            stripped = line.strip()
            if stripped.startswith(('#', '//', '/*', '*')) or (
                (stripped.startswith(('"', "'")) and stripped.endswith(('"', "'")))
            ):
                severity = Severity.LOW
            findings.append(
                Finding(
                    path=record.path,
                    lineno=lineno,
                    col_offset=col,
                    algorithm=algo,
                    evidence=token,
                    severity=severity,
                )
            )
    return findings
