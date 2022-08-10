from __future__ import annotations

import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import JSON, TIMESTAMP

from ftrack_webhooks.extentions import db


class EventLogItem(db.Model):
    id = db.Column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    entity_id = db.Column(UUID(as_uuid=False), nullable=False, unique=False)
    entity_type = db.Column(db.String(255), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    time = db.Column(TIMESTAMP(timezone=True), nullable=False)
    payload = db.Column(JSON, nullable=False)
