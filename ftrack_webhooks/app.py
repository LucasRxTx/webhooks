from __future__ import annotations

from logging import getLogger

import flask

from ftrack_webhooks import extentions
from ftrack_webhooks.api import blueprints

logger = getLogger(__name__)


def create_app():
    app = flask.Flask(__name__)
    app.config.from_object("ftrack_webhooks.settings.FlaskConfig")

    blueprints.add_all(app)
    extentions.register_app(app)

    with app.app_context():
        extentions.db.create_all()

    return app
