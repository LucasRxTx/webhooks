from __future__ import annotations

import http
from logging import getLogger
from typing import Any, cast

import flask

from ftrack_webhooks.services import webhooks as webhooks_service
from ftrack_webhooks.types import FTrackEvent

logger = getLogger(__name__)
blueprint = flask.Blueprint("webhooks", __name__)


@blueprint.route("/webhooks/event", methods=["POST"])
def accept_webhook() -> tuple[str, int]:
    logger.info("ingesting event")
    event: dict = cast(dict[str, Any], flask.request.json)
    request = flask.request

    is_authenticated = webhooks_service.authenticate(request, event)
    if not is_authenticated:
        return "", http.HTTPStatus.UNAUTHORIZED

    is_authroized = webhooks_service.authroize(request, event)
    if not is_authroized:
        return "", http.HTTPStatus.FORBIDDEN

    if "action" not in event:
        # TODO: more validation required
        webhooks_service.report_bad_event(event)
        return "", http.HTTPStatus.BAD_REQUEST

    ftrack_event: FTrackEvent = cast(FTrackEvent, event)

    webhooks_service.handle_event(ftrack_event)

    return "", http.HTTPStatus.CREATED
