from __future__ import annotations

from typing import Literal, TypedDict


class FTrackCreateEvent(TypedDict):
    action: Literal["create"]
    entity_type: str
    payload: dict
    time: str


class FTrackUpdateEvent(TypedDict):
    action: Literal["update"]
    entity_type: str
    id: str
    modified_fields: list[str]
    payload: dict
    time: str


FTrackEvent = FTrackCreateEvent | FTrackUpdateEvent


class CreateEventLogRequest(TypedDict):
    id: str
    action: str
    entity_type: str
    payload: dict
    time: str
