import flask

from ftrack_webhooks.api import dashboard, events, webhooks

__blueprints = (
    dashboard.blueprint,
    events.blueprint,
    webhooks.blueprint,
)


def add_all(app: flask.Flask):
    """Register all blueprints with flask app."""
    for blueprint in __blueprints:
        app.register_blueprint(blueprint)
