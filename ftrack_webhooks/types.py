from __future__ import annotations

from typing import Literal, TypedDict


ActionUpdate = Literal["update"]
ActionCreate = Literal["create"]
ActionType = ActionUpdate | ActionCreate


class EventLogItem(TypedDict):
    id: str
    entity_id: str
    entity_type: str
    action: ActionType
    time: str
    payload: dict


class FTrackCreateEvent(TypedDict):
    action: ActionCreate
    entity_type: str
    payload: dict
    time: str


class FTrackUpdateEvent(TypedDict):
    action: ActionUpdate
    entity_type: str
    id: str
    modified_fields: list[str]
    payload: dict
    time: str


FTrackEvent = FTrackCreateEvent | FTrackUpdateEvent


class CreateEventLogRequest(TypedDict):
    id: str
    action: ActionType
    entity_type: str
    payload: dict
    time: str
