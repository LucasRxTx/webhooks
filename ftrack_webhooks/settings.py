import os

markdown_extensions = [
    "codehilite",
    "fenced_code",
    "footnotes",
    "admonition",
    "tables",
    "smarty",
    "toc",
    "sane_lists",
]
"""Extentions to enable in the markdown package.

https://python-markdown.github.io/extensions/
"""


class FlaskConfig:
    """Configuration for the flask app.

    For more configuration options for flask see:
    https://flask.palletsprojects.com/en/2.1.x/config/

    For more configuration options for flask-sqlalchemy see:
    https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/
    """

    SECRET_KEY = os.environ["SECRET_KEY"]
    FLASK_ENV = os.environ["FLASK_ENV"]
    DEBUG = False if os.environ["DEBUG"] == "false" else True
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    SQLALCHEMY_ECHO = True if os.environ["SQLALCHEMY_ECHO"] == "true" else False
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        False if os.environ["SQLALCHEMY_TRACK_MODIFICATIONS"] == "false" else True
    )
