from __future__ import annotations

import abc
import http
import json
import uuid
from datetime import datetime
from logging import getLogger
from typing import Any, Literal, Type, TypedDict, cast

import flask
import flask_sqlalchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import JSON, TIMESTAMP
from typing_extensions import Never


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
