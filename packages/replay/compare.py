from __future__ import annotations

from packages.replay.models import ReplayRecord, ReplayResponseRecord


class ReplayComparator:
    """
    Compares the original recorded response with a replayed response.

    Sprint 1 intentionally keeps comparison simple and inspectable.
    """

    def compare(
        self,
        *,
        original: ReplayRecord,
        replayed: ReplayResponseRecord,
        replayed_provider: str,
        replayed_model: str,
    ) -> dict[str, object]:
        original_content = original.response.content
        replayed_content = replayed.content

        original_eval = original.response.evaluation
        replayed_eval = replayed.evaluation

        original_score = self._extract_reliability_score(original_eval)
        replayed_score = self._extract_reliability_score(replayed_eval)

        return {
            "content_exact_match": original_content == replayed_content,
            "original_content_length": len(original_content),
            "replayed_content_length": len(replayed_content),
            "content_length_delta":
                len(replayed_content) - len(original_content),
            "same_provider": original.request.provider == replayed_provider,
            "same_model": original.request.resolved_model == replayed_model,
            "original_provider": original.request.provider,
            "replayed_provider": replayed_provider,
            "original_model": original.request.resolved_model,
            "replayed_model": replayed_model,
            "original_reliability_score": original_score,
            "replayed_reliability_score": replayed_score,
            "reliability_score_delta": (
                None
                if original_score is None or replayed_score is None
                else round(replayed_score - original_score, 4)
            ),
        }

    @staticmethod
    def _extract_reliability_score(evaluation:
                                   dict[str, object]) -> float | None:
        raw = evaluation.get("reliability_score")
        if raw is None:
            return None

        try:
            return float(raw)
        except (TypeError, ValueError):
            return None
