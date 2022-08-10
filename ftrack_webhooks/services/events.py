from __future__ import annotations

from datetime import datetime
from typing import Any, Type

from ftrack_webhooks.models import EventLogItem
from ftrack_webhooks.repositories import EventRepository, EventRepositoryAbstract


class EventService:
    REPOSITORY: Type[EventRepositoryAbstract] = EventRepository

    def __init__(self):
        self.__repository = self.REPOSITORY()

    def get(self, event_id: str) -> EventLogItem | None:
        return self.__repository.get(event_id)

    def get_event_aggrigation(self, entity_id: str) -> dict | None:
        entity_log_items = self.__repository.get_all_entity_logs(entity_id)
        return self.__play_events(entity_log_items)

    def get_all_event_logs(self) -> list[EventLogItem]:
        return self.__repository.get_all_event_logs()

    def get_all_event_logs_for_entity(
        self,
        entity_id,
        stop: datetime | None = None,
    ) -> list[EventLogItem]:
        return self.__repository.get_all_entity_logs(entity_id, stop)

    def delete_old_events(self) -> None:
        """Delete old events."""
        self.__repository.delete_old_events()
        return None

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
