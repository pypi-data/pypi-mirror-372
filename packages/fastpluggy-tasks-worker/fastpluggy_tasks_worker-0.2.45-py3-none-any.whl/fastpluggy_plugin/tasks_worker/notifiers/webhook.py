import httpx
from ..notifiers.base import BaseNotifier, NotificationEvent
from ..schema.task_event import event_matches


class WebHookNotifier(BaseNotifier):
    name = 'webhook_notifier'
    def notify(self, event: NotificationEvent):
        if not event_matches(event_type=event.event_type , rule_events=self.events):
            return
        try:
            payload = {
                "text": f"*[{event.event_type.upper()}]* `{event.name}` → {event.message}"
            }
            httpx.post(self.config["webhook_url"], json=payload, timeout=5)
        except Exception as e:
            print(f"[WEBHOOK NOTIFIER ERROR] {e}")