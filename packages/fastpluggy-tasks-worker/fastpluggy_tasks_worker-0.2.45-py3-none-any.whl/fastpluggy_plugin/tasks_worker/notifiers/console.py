# notifiers/console.py

from ..notifiers.base import BaseNotifier, NotificationEvent, LogStreamEvent
from ..schema.task_event import event_matches


class ConsoleNotifier(BaseNotifier):
    name: str = "console_notifier"

    def notify(self, event: NotificationEvent):
        if not event_matches(event_type=event.event_type , rule_events=self.events):
            return
        print(f"[NOTIFY:{event.task_id}] [{event.timestamp}] [{event.event_type.upper()}] {event.name} : {event.message}")
        if event.error:
            print(f"[ERROR] {event.error}")

    def handle_log(self, event: LogStreamEvent):
        print(f"[LOG:{event.task_id}] [{event.record.levelname}] {event.record.getMessage()}")
