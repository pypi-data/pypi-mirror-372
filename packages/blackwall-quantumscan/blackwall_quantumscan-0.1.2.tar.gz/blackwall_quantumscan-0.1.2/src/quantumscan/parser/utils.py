from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Tuple, Optional, Iterable

from .models import ErrorCode

LANG_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".go": "go",
}

EXCLUDE_DIRS = {".git", "node_modules", "venv", "__pycache__"}
MAX_SIZE = 5 * 1024 * 1024


def detect_language(ext: str) -> str:
    return LANG_MAP.get(ext.lower(), "")


def is_supported_ext(ext: str, allowed: Iterable[str] | None = None) -> bool:
    allowed = set(allowed) if allowed else set(LANG_MAP.keys())
    return ext.lower() in allowed


def should_skip_dir(name: str) -> bool:
    return name in EXCLUDE_DIRS


def normalize_algo_name(name: str) -> str:
    """Normalize algorithm aliases to canonical form."""
    key = name.replace("-", "").replace("_", "").replace(" ", "").lower()
    if key.startswith("rsa") and key[3:].isdigit():
        key = "rsa"
    mapping = {
        "rsa": "RSA",
        "rsapss": "RSA-PSS",
        "ecdh": "ECDH",
        "ecdsa": "ECDSA",
        "x25519": "X25519",
        "curve25519": "X25519",
        "sha1": "SHA-1",
        "md5": "MD5",
    }
    return mapping.get(key, name.upper())


def read_text_safely(path: Path) -> Tuple[Optional[str], Optional[ErrorCode]]:
    """Read a file and return text; on decode issues returns ``DECODE_ERROR``."""
    try:
        data = path.read_bytes()
    except OSError as e:
        return None, ErrorCode.IO_ERROR
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            text = data.decode(encoding)
            if "\x00" in text:
                return None, ErrorCode.DECODE_ERROR
            if text.startswith("\ufeff"):
                text = text[1:]
            return text, None
        except UnicodeDecodeError:
            continue
    return None, ErrorCode.DECODE_ERROR


def sha256sum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_read_text(path: Path) -> Tuple[Optional[str], Optional[ErrorCode]]:
    """Alias for read_text_safely for backward compatibility."""
    return read_text_safely(path)
