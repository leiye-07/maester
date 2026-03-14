from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from apps.api.deps import get_replay_replayer, get_replay_store
from packages.replay.replayer import ReplayReplayer
from packages.replay.store import ReplayStore

router = APIRouter(prefix="/v1/replays", tags=["replays"])


class ReplayRecordResponse(BaseModel):
    record: dict


class ReplayRunResponse(BaseModel):
    result: dict


@router.get("/{request_id}", response_model=ReplayRecordResponse)
def get_replay_record(
    request_id: str,
    replay_store: ReplayStore = Depends(get_replay_store),
) -> ReplayRecordResponse:
    try:
        record = replay_store.get(request_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ReplayRecordResponse(record=record.as_dict())


@router.post("/{request_id}/run", response_model=ReplayRunResponse)
def run_replay(
    request_id: str,
    replay_store: ReplayStore = Depends(get_replay_store),
    replay_replayer: ReplayReplayer = Depends(get_replay_replayer),
) -> ReplayRunResponse:
    try:
        record = replay_store.get(request_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    result = replay_replayer.replay(record)
    return ReplayRunResponse(result=result.as_dict())
