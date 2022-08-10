from __future__ import annotations

from logging import getLogger

import flask

from ftrack_webhooks import mappings
from ftrack_webhooks.services.events import EventService

logger = getLogger(__name__)
blueprint = flask.Blueprint("dashboard", __name__)


@blueprint.route("/dashboard", methods=["GET"])
def event_dashboard():
    event_service = EventService()
    event_logs = event_service.get_all_event_logs()
    events = [
        mappings.event_log_item_to_dictionary(event_log) for event_log in event_logs
    ]
    table_headers = None if not events else events[0].keys()

    return flask.render_template(
        "dashboard.html",
        events=events,
        table_headers=table_headers,
    )


@blueprint.route("/dashboard/<string:entity_id>", methods=["GET"])
def event_dashboard_for_entity(entity_id: str):
    event_service = EventService()
    event_logs = event_service.get_all_event_logs_for_entity(entity_id)
    events = [
        mappings.event_log_item_to_dictionary(event_log) for event_log in event_logs
    ]
    table_headers = None if not events else events[0].keys()

    return flask.render_template(
        "dashboard.html",
        events=events,
        table_headers=table_headers,
    )
