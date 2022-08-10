import abc
from datetime import datetime, timezone, timedelta

from ftrack_webhooks.extentions import db
from ftrack_webhooks.models import EventLogItem
from ftrack_webhooks.types import CreateEventLogRequest


class EventRepositoryAbstract(abc.ABC):
    @abc.abstractmethod
    def get(self, event_id: str) -> EventLogItem | None:
        ...

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
    def delete_old_events(self) -> None:
        ...

    @abc.abstractmethod
    def save(self) -> None:
        ...


class EventRepository(EventRepositoryAbstract):
    DB_SESSION_FACTORY = db.session

    def __init__(self):
        self.__session = self.DB_SESSION_FACTORY()

    def get(self, event_id: str) -> EventLogItem | None:
        return self.__session.query(EventLogItem).filter_by(id=event_id).one_or_none()

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

    def delete_old_events(self) -> None:
        """Delete events older than 7 days."""
        too_old = datetime.now(tz=timezone.utc) - timedelta(days=7)
        self.__session.query(EventLogItem).filter(EventLogItem.time < too_old).delete()
        self.__session.commit()

    def save(self) -> None:
        self.__session.commit()
        return None
