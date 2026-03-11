from __future__ import annotations

from packages.prompt_registry.hashing import hash_prompt_content
from packages.prompt_registry.models import PromptLookup, RenderedPrompt
from packages.prompt_registry.registry import PromptRegistry


class PromptService:
    def __init__(self, registry: PromptRegistry) -> None:
        self.registry = registry

    def render(
        self,
        *,
        name: str,
        variables: dict[str, object],
        version: str | None = None,
    ) -> RenderedPrompt:
        template = self.registry.get(PromptLookup(name=name, version=version))
        content = template.template.format(**variables)
        prompt_hash = hash_prompt_content(content)

        return RenderedPrompt(
            name=template.name,
            version=template.version,
            template=template.template,
            variables=variables,
            content=content,
            hash=prompt_hash,
        )