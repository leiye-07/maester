"""
ID utilities.

Responsibilities:
- generate globally unique IDs
- ensure collision-safe identifiers
- support tracing across services

Future:
- ULID based identifiers
- request id propagation helpers
"""

from __future__ import annotations

import uuid


def new_id() -> str:
    return uuid.uuid4().hex

def prefixed_id(prefix: str) -> str:
    return f"{prefix}_{new_id()}"