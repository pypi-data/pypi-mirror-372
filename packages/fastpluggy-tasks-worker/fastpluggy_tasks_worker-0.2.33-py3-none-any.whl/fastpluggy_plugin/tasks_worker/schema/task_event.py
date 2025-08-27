from enum import Enum
from typing import List, Union


class TaskEvent(str, Enum):
    # TODO : add queued status
    # TODO: uniform and also use TaskStatus
    task_started = "task_started"
    task_success = "task_success"
    task_failed = "task_failed"
    task_progress = "task_progress"
    task_canceled = "task_canceled"
# more event types (e.g., task_queued, task_interrupted, etc.) ?
    logs = "logs"

    # New unified extensions
    status = "status"         # For general status updates
    heartbeat = "heartbeat"   # For periodic pings if needed

    # Special value for wildcard matching all events
    ALL = "*"

    CONTEXT = "context"

    @classmethod
    def all_values(cls) -> List[str]:
        """Return all valid event types."""
        return [e.value for e in cls ]
    #
    # @classmethod
    # def is_valid(cls, event: str) -> bool:
    #     """Return True if event is a known TaskEvent or wildcard."""
    #     return event == cls.ALL or event in cls._value2member_map_
    #
    # @classmethod
    # def validate_list(cls, event_list: List[str]) -> List[str]:
    #     """Raise ValueError if any entry is invalid."""
    #     for event in event_list:
    #         if not cls.is_valid(event):
    #             raise ValueError(f"Invalid TaskEvent: {event}")
    #     return event_list


def event_matches(rule_events: List[str], event_type: Union[str, TaskEvent]) -> bool:
    """
    Returns True if the rule events contain the given event or a wildcard.
    """
    return TaskEvent.ALL in rule_events or str(event_type) in rule_events
