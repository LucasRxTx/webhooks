from __future__ import annotations
import abc
import json
from typing_extensions import Never

from sqlalchemy.types import TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID
from typing import TypedDict, Type, Literal, Any, cast
import flask
import flask_sqlalchemy
import uuid
from datetime import datetime
from logging import getLogger
import http

logger = getLogger(__name__)

app = flask.Flask(__name__)

app.config.from_object("ftrack_webhooks.settings.FlaskConfig")
db = flask_sqlalchemy.SQLAlchemy(app)


class FTrackCreateEvent(TypedDict):
    action: Literal["create"]
    entity_type: str
    payload: dict
    time: str


class FTrackUpdateEvent(TypedDict):
    action: Literal["update"]
    entity_type: str
    id: str
    modified_fields: list[str]
    payload: dict
    time: str


FTrackEvent = FTrackCreateEvent | FTrackUpdateEvent


class EventLogItem(db.Model):
    id = db.Column(UUID(as_uuid=False), primary_key=True, default=uuid.uuid4)
    entity_id = db.Column(UUID(as_uuid=False), nullable=False, unique=False)
    entity_type = db.Column(db.String(255), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    time = db.Column(TIMESTAMP(timezone=True), nullable=False)
    payload = db.Column(JSON, nullable=False)


class CreateEventLogRequest(TypedDict):
    id: str
    action: str
    entity_type: str
    payload: dict
    time: str


class EventRepositoryAbstract(abc.ABC):
    @abc.abstractmethod
    def get_all_entity_logs(
        self,
        entity_id: str,
        stop: datetime | None = None,
    ) -> list[EventLogItem]:
        ...

    @abc.abstractmethod
    def get_all_event_logs(self) -> list[EventLogItem]:
        ...

    @abc.abstractmethod
    def create(self, data: CreateEventLogRequest) -> None:
        ...

    @abc.abstractmethod
    def save(self) -> None:
        ...


class EventRepository(EventRepositoryAbstract):
    DB_SESSION_FACTORY = db.session

    def __init__(self):
        self.__session = self.DB_SESSION_FACTORY()

    def get_all_entity_logs(
        self,
        entity_id: str,
        stop: datetime | None = None,
    ) -> list[EventLogItem]:
        query = self.__session.query(EventLogItem).filter_by(entity_id=entity_id)
        if stop:
            query = query.filter(EventLogItem.time <= stop)

        return query.order_by(EventLogItem.time.asc()).all()

    def get_all_event_logs(self) -> list[EventLogItem]:
        return self.__session.query(EventLogItem).all()

    def create(self, data: CreateEventLogRequest) -> None:
        event_log_item = EventLogItem(
            entity_id=data["id"],
            entity_type=data["entity_type"],
            action=data["action"],
            time=data["time"],
            payload=data["payload"],
        )
        self.__session.add(event_log_item)
        return None

    def save(self) -> None:
        self.__session.commit()
        return None


class EventService:
    REPOSITORY: Type[EventRepositoryAbstract] = EventRepository

    def __init__(self):
        self.__repository = self.REPOSITORY()

    def get_event_aggrigation(self, entity_id: str) -> dict | None:
        entity_log_items = self.__repository.get_all_entity_logs(entity_id)
        return self.__play_events(entity_log_items)

    def get_all_event_logs(self) -> list[EventLogItem]:
        return self.__repository.get_all_event_logs()

    def get_all_event_logs_for_entity(
        self, entity_id, stop: datetime | None = None
    ) -> list[EventLogItem]:
        return self.__repository.get_all_entity_logs(entity_id, stop)

    def __play_events(
        self,
        events: list[EventLogItem],
    ) -> dict[str, Any] | None:
        if events and events[0].action != "create":
            raise RuntimeError(
                "Aggregate potentially corrupted. First event is not a create action."
            )

        data = {}
        first_event = True
        for event in events:
            if event.action == "update" or first_event and event.action == "create":
                data.update(event.payload)
            else:
                if not first_event:
                    raise RuntimeError(
                        "Aggregate potentially corrupted.  "
                        "Got create action after update action.",
                    )
            first_event = False

        return data


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


def event_log_item_to_dictionary(event_log_item: EventLogItem) -> dict:
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


def handle_create_event(event: FTrackCreateEvent) -> None:
    """Handle a FTrack create event."""
    repo = EventRepository()
    create_request = create_event_to_create_event_log_request(event)
    repo.create(create_request)
    repo.save()
    return None


def handle_update_event(event: FTrackUpdateEvent) -> None:
    """Handle a FTrack update event."""
    repo = EventRepository()
    create_request = update_event_to_create_event_log_request(event)
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


DEFAULT_HEADERS = {"Content-Type": "application/json"}


@app.route("/dashboard", methods=["GET"])
def event_dashboard():
    event_service = EventService()
    event_logs = event_service.get_all_event_logs()
    events = [event_log_item_to_dictionary(event_log) for event_log in event_logs]
    table_headers = None if not events else events[0].keys()

    return flask.render_template(
        "dashboard.html",
        events=events,
        table_headers=table_headers,
    )


@app.route("/dashboard/<string:entity_id>", methods=["GET"])
def event_dashboard_for_entity(entity_id: str):
    event_service = EventService()
    event_logs = event_service.get_all_event_logs_for_entity(entity_id)
    events = [event_log_item_to_dictionary(event_log) for event_log in event_logs]
    table_headers = None if not events else events[0].keys()

    return flask.render_template(
        "dashboard.html",
        events=events,
        table_headers=table_headers,
    )


@app.route("/events", methods=["GET"])
def all_events() -> tuple[str, int, dict]:
    event_service = EventService()
    event_logs = event_service.get_all_event_logs()

    return (
        json.dumps(
            event_logs,
            default=event_log_item_to_dictionary,
        ),
        200,
        DEFAULT_HEADERS,
    )


@app.route("/events/<string:entity_id>", methods=["GET"])
def all_events_for_entity(entity_id: str) -> tuple[str, int, dict]:
    event_service = EventService()
    entity_event_logs = event_service.get_all_event_logs_for_entity(entity_id)

    return (
        json.dumps(
            entity_event_logs,
            default=event_log_item_to_dictionary,
        ),
        200,
        DEFAULT_HEADERS,
    )


@app.route("/aggrigates/<string:entity_id>", methods=["GET"])
def get_aggrigate_by_id(entity_id: str) -> tuple[str | dict, int, dict]:
    logger.warning("getting aggregate")
    event_service = EventService()
    aggrigate = event_service.get_event_aggrigation(entity_id)

    if aggrigate is None:
        return "", 404, DEFAULT_HEADERS

    return aggrigate, 200, DEFAULT_HEADERS


@app.route("/webhooks/event", methods=["POST"])
def accept_webhook() -> tuple[str, int]:
    logger.info("ingesting event")
    event: dict = cast(dict[str, Any], flask.request.json)
    request = flask.request

    is_authenticated = authenticate(request, event)
    if not is_authenticated:
        return "", http.HTTPStatus.UNAUTHORIZED

    is_authroized = authroize(request, event)
    if not is_authroized:
        return "", http.HTTPStatus.FORBIDDEN

    if "action" not in event:
        # TODO: more validation required
        report_bad_event(event)
        return "", http.HTTPStatus.BAD_REQUEST

    ftrack_event: FTrackEvent = cast(FTrackEvent, event)

    handle_event(ftrack_event)

    return "", http.HTTPStatus.CREATED
