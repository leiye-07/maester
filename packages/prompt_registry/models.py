from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    name: str
    version: str
    template: str
    description: str | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RenderedPrompt:
    name: str
    version: str
    template: str
    variables: dict[str, Any]
    content: str
    hash: str


@dataclass(frozen=True, slots=True)
class PromptLookup:
    name: str
    version: str | None = None