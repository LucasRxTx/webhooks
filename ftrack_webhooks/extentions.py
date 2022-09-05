"""Flask Extentions.

Adding an extention to the ``__extentions_registry`` will
late init the extention with the flask app when ``create_app``
is called.
"""

import flask
import flask_sqlalchemy

db = flask_sqlalchemy.SQLAlchemy()


__extentions_registry = (db,)
"""Add extention instances here to late initialize with flask app."""


def register_app(app: flask.Flask) -> None:
    """Register all extentions with flask app."""
    for extention in __extentions_registry:
        extention.init_app(app)
