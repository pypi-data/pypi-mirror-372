from __future__ import annotations

import datetime
import hashlib
import json
import mimetypes
from typing import Any


def sha256_path(path: str) -> str:
    """SHA-256 hex of a file on disk."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def iso8601_now() -> str:
    """UTC timestamp in strict ISO-8601 (no micros, with Z)."""
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def guess_mime(path: str) -> str:
    """Best-effort MIME type for a path."""
    m, _ = mimetypes.guess_type(path)
    return m or "application/octet-stream"


def _to_str(value: Any) -> str:
    """Convert *anything* to a string; prefer human fields if dict."""
    if value is None:
        return ""
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        # Prefer typical identity fields
        for key in ("name", "issuer", "title", "subject"):
            v = value.get(key)
            if isinstance(v, str):
                return v
        # Fallback: JSON stringify the dict (still a string)
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def format_identity(value: Any) -> str:
    """
    Always return a **string** identity, normalised:
    - trim whitespaces
    - lowercase
    Accepts str, dict, or any type. Never returns a dict.
    """
    s = _to_str(value).strip()
    return s.lower()
