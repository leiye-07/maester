from __future__ import annotations

from packages.prompt_registry.models import PromptTemplate


def default_prompt_templates() -> list[PromptTemplate]:
    return [
        PromptTemplate(
            name="system_summary",
            version="v1",
            template=(
                "You are a production AI assistant.\n"
                "Summarize the following system event clearly:\n\n"
                "{event_text}"
            ),
            description="Basic system event summarization prompt.",
            tags=("summary", "system"),
        ),
        PromptTemplate(
            name="system_summary",
            version="v2",
            template=(
                "You are a production AI assistant focused on reliability.\n"
                "Summarize the following system event.\n"
                "Be concise, mention operational impact, and keep the tone factual.\n\n"
                "{event_text}"
            ),
            description="Improved reliability-oriented system summary prompt.",
            tags=("summary", "system", "reliability"),
        ),
    ]