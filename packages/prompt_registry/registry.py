from __future__ import annotations

from packages.prompt_registry.models import PromptLookup, PromptTemplate


class PromptRegistry:
    def __init__(self, templates: list[PromptTemplate] | None = None) -> None:
        self._templates: dict[tuple[str, str], PromptTemplate] = {}

        for template in templates or []:
            self.register(template)

    def register(self, template: PromptTemplate) -> None:
        key = (template.name, template.version)
        self._templates[key] = template

    def get(self, lookup: PromptLookup) -> PromptTemplate:
        if lookup.version is not None:
            key = (lookup.name, lookup.version)
            if key not in self._templates:
                raise KeyError(f"Prompt not found: {lookup.name}@{lookup.version}")
            return self._templates[key]

        matches = [
            template
            for (name, _), template in self._templates.items()
            if name == lookup.name
        ]
        if not matches:
            raise KeyError(f"Prompt not found: {lookup.name}")

        # Sprint 1 policy: latest by lexical version sort
        matches.sort(key=lambda x: x.version, reverse=True)
        return matches[0]

    def list_prompt_versions(self, name: str) -> list[str]:
        versions = [
            version
            for (template_name, version) in self._templates.keys()
            if template_name == name
        ]
        return sorted(versions, reverse=True)