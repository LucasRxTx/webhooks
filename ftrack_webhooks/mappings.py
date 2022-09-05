from ftrack_webhooks.models import EventLogItem
from ftrack_webhooks.types import (
    CreateEventLogRequest,
    EventLogItem,
    FTrackCreateEvent,
    FTrackUpdateEvent,
)


def create_event_to_create_event_log_request(
    event: FTrackCreateEvent,
) -> CreateEventLogRequest:
    """Map a ``FTrackCreateEvent`` to an ``EventLogItem``."""

    return CreateEventLogRequest(
        id=event["payload"]["id"],
        entity_type=event["entity_type"],
        action=event["action"],
        time=event["time"],
        payload=event["payload"],
    )


def event_log_item_to_dictionary(event_log_item: EventLogItem) -> EventLogItemDict:
    """Map and ``EventLogItem`` to a plain dictionary."""
    return dict(
        id=event_log_item.id,
        entity_id=event_log_item.entity_id,
        entity_type=event_log_item.entity_type,
        action=event_log_item.action,
        time=event_log_item.time.isoformat(),
        payload=event_log_item.payload,
    )


def update_event_to_create_event_log_request(
    event: FTrackUpdateEvent,
) -> CreateEventLogRequest:
    """Map an ``FTrackUpdateEvent`` to an ``EventLogItem``."""

    return CreateEventLogRequest(
        id=event["id"],
        entity_type=event["entity_type"],
        action=event["action"],
        time=event["time"],
        payload=event["payload"],
    )
