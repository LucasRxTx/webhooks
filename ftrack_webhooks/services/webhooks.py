from __future__ import annotations

from typing_extensions import Never

import flask
from logging import getLogger
from ftrack_webhooks.types import (
    FTrackCreateEvent,
    FTrackUpdateEvent,
    FTrackEvent,
)
from ftrack_webhooks import repositories
from ftrack_webhooks import mappings


logger = getLogger(__name__)


def authenticate(request: flask.Request, data: dict | None = None) -> bool:
    """Is the requester authenticated with our systems?

    Check API keys, HMAC, ip whitelist, ect.
    """
    data = data or None
    return True


def authroize(request: flask.Request, data: dict | None = None) -> bool:
    """Is the requester authroized to take this action?

    Can the given user have the roles and permissions to do what
    they are trying to do?
    """
    data = data or None
    return True


def handle_create_event(event: FTrackCreateEvent) -> None:
    """Handle a FTrack create event."""
    repo = repositories.EventRepository()
    create_request = mappings.create_event_to_create_event_log_request(event)
    repo.create(create_request)
    repo.save()
    return None


def handle_update_event(event: FTrackUpdateEvent) -> None:
    """Handle a FTrack update event."""
    repo = repositories.EventRepository()
    create_request = mappings.update_event_to_create_event_log_request(event)
    repo.create(create_request)
    repo.save()
    return None


def default_handler(event: Never) -> None:
    """Handler that is called if a ``FTrackEvent`` has no handler."""
    logger.info("Unhandled event", extra=event)
    return None


def report_bad_event(event: dict) -> None:
    """A malformed ``FTrackEvent`` has entered the system."""
    # if using sentry middleware, setup sanitation as appropriate.
    logger.warning("Bad event", extra=event)
    return None


def handle_event(event: FTrackEvent) -> None:
    """Dispatch an ``FTrackEvent`` to an event handler."""

    # Note: a Gaurd is used instead of a dictionary for typing purpouses.
    if event["action"] == "create":
        handle_create_event(event)
    elif event["action"] == "update":
        handle_update_event(event)
    else:
        default_handler(event)

    return None
