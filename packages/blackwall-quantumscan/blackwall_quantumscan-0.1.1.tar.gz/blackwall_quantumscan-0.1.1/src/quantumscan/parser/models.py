from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ErrorCode(str, Enum):
    TOO_LARGE = "too_large"
    IO_ERROR = "io_error"
    DECODE_ERROR = "decode_error"
    SYMLINK_LOOP = "symlink_loop"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class FileRecord:
    path: str
    ext: str
    language: str
    size: int
    sha256: str
    line_count: int
    modified_ts: float
    content: Optional[str]
    error_code: Optional[ErrorCode] = None
    error_detail: Optional[str] = None


@dataclass
class Finding:
    path: str
    lineno: int
    col_offset: int
    algorithm: str
    evidence: str  # raw token evidence for CLI output
    severity: Severity


@dataclass
class FindingError:
    path: str
    code: str
    message: str
