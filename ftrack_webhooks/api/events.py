from __future__ import annotations

import json
from logging import getLogger

import flask

from ftrack_webhooks import mappings
from ftrack_webhooks.services.events import EventService

logger = getLogger(__name__)
blueprint = flask.Blueprint("events", __name__)
DEFAULT_HEADERS = {"Content-Type": "application/json"}


@blueprint.route("/events", methods=["GET"])
def all_events() -> tuple[str, int, dict]:
    event_service = EventService()
    event_logs = event_service.get_all_event_logs()

    return (
        json.dumps(
            event_logs,
            default=mappings.event_log_item_to_dictionary,
        ),
        200,
        DEFAULT_HEADERS,
    )


@blueprint.route("/events/<string:event_id>", methods=["GET"])
def get_event_log_by_id(event_id: str) -> tuple[str, int, dict]:
    event_service = EventService()
    event_log = event_service.get(event_id)

    if event_log is None:
        return "", 404, DEFAULT_HEADERS

    return (
        json.dumps(
            mappings.event_log_item_to_dictionary(event_log),
        ),
        200,
        DEFAULT_HEADERS,
    )


@blueprint.route("/entities/<string:entity_id>", methods=["GET"])
def get_entity_event_logs(entity_id: str) -> tuple[str, int, dict]:
    event_service = EventService()
    event_logs = event_service.get_all_event_logs_for_entity(entity_id)

    return (
        json.dumps(
            event_logs,
            default=mappings.event_log_item_to_dictionary,
        ),
        200,
        DEFAULT_HEADERS,
    )


@blueprint.route("/aggrigates/<string:entity_id>", methods=["GET"])
def get_aggrigate_by_id(entity_id: str) -> tuple[str | dict, int, dict]:
    logger.warning("getting aggregate")
    event_service = EventService()
    aggrigate = event_service.get_event_aggrigation(entity_id)

    if aggrigate is None:
        return "", 404, DEFAULT_HEADERS

    return aggrigate, 200, DEFAULT_HEADERS
