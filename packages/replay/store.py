from __future__ import annotations

from packages.replay.models import ReplayRecord


class ReplayStore:
    """
    In-memory replay store for Sprint 1.

    This keeps the implementation simple and easy to understand.
    Later versions can replace this with:
    - file-backed JSON storage
    - SQLite/Postgres
    - object storage
    """

    def __init__(self) -> None:
        self._records: dict[str, ReplayRecord] = {}

    def save(self, record: ReplayRecord) -> None:
        self._records[record.request_id] = record

    def get(self, request_id: str) -> ReplayRecord:
        if request_id not in self._records:
            raise KeyError(f"Replay record not found: {request_id}")
        return self._records[request_id]

    def list_records(self) -> list[ReplayRecord]:
        return sorted(
            self._records.values(),
            key=lambda record: record.created_at,
            reverse=True,
        )

    def exists(self, request_id: str) -> bool:
        return request_id in self._records

    def size(self) -> int:
        return len(self._records)
