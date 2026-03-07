"""
Security utilities.

Responsibilities:
- API key hashing
- API key verification
- secret handling helpers

Future features:
- key rotation
- key scopes
- secure token generation
"""
from __future__ import annotations

import hashlib
import hmac
import os


def hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def constant_time_equals(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)

def mask_secret(value: str, visible_suffix: int = 4) -> str:
    if len(value) <= visible_suffix:
        return "*" * len(value)
    return "*" * (len(value) - visible_suffix) + value[-visible_suffix:]
