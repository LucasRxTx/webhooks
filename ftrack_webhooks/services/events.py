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
        """Get a sepecific event."""
        return self.__repository.get(event_id)

    def get_event_aggrigation(self, entity_id: str) -> dict | None:
        """Return the state of an entity after playing all events."""
        entity_log_items = self.__repository.get_all_entity_logs(entity_id)
        return self.__play_events(entity_log_items)

    def get_all_event_logs(self) -> list[EventLogItem]:
        """Get all event logs."""
        return self.__repository.get_all_event_logs()

    def get_all_event_logs_for_entity(
        self,
        entity_id,
        stop: datetime | None = None,
    ) -> list[EventLogItem]:
        """Get all event logs for a specific entity."""
        return self.__repository.get_all_entity_logs(entity_id, stop)

    def delete_old_events(self) -> None:
        """Delete old events."""
        self.__repository.delete_old_events()
        return None

    def __play_events(
        self,
        events: list[EventLogItem],
    ) -> dict[str, Any] | None:
        """Play events, storing the current state into a dict.

        Returns:
            dict: The current state of an object given the supplied events.
        """
        if events and events[0].action != "create":
            raise RuntimeError(
                "Aggregate potentially corrupted. First event is not a create action."
            )

        data = {}
        for i, event in enumerate(events):
            if event.action == "update" or i == 0 and event.action == "create":
                data.update(event.payload)
            else:
                if i != 0:
                    raise RuntimeError(
                        "Aggregate potentially corrupted.  "
                        "Got create action after update action.",
                    )

        return data
