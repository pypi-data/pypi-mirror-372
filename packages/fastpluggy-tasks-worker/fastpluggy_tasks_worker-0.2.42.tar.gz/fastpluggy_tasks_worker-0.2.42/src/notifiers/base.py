# notifiers/base.py
from dataclasses import dataclass, field
from datetime import datetime
from logging import LogRecord
from typing import Optional, List, Any

from ..schema.task_event import TaskEvent


@dataclass
class NotificationEvent:
    event_type: str  # task_started, task_success, task_failed
    task_id: str
    name: str
    function: str
    timestamp: datetime
    message: str
    success: Optional[bool] = None
    error: Optional[str] = None


@dataclass
class LogStreamEvent:
    task_id: str
    record: LogRecord
    event_type: str = field(default=TaskEvent.logs.value)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class BaseNotifier:
    name: str

    def __init__(self, config: dict = None, events: List[str | TaskEvent] = None):
        self.config = config
        self.events = events or []

    def __str__(self):
        return f'<{self.__class__.__name__}: {self.name}>'

    def notify(self, event: NotificationEvent):
        raise NotImplementedError

    def handle_log(self, event: LogStreamEvent):
        # Optional to override
        pass

    def on_context(self, task_id: str, key: str, value: Any):
        pass  # Optional for most

    def on_task_init(self, task_id: str):
        """
        Optional hook for setting up resources at task submission time.
        Useful for setup like live log queues.
        """
        pass

    def on_task_done(self, task_id: str):
        """Optional hook for cleaning up resources after task completion."""
        pass

    @property
    def can_handle_log(self) -> bool:
        return callable(getattr(self, "handle_log", None)) and \
            self.__class__.handle_log is not BaseNotifier.handle_log

    @property
    def configurable_events(self) -> list[str]:
        return TaskEvent.all_values()


    def export_for_factory(self):
        return {
            "name": self.name,
            "class": f"{self.__class__.__module__}.{self.__class__.__qualname__}",
            "can_handle_log": self.can_handle_log,
            "configurable_events": self.configurable_events,
            **self.__dict__,  # Merge instance fields like config, events
        }
