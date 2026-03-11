from __future__ import annotations

import hashlib


def hash_prompt_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()