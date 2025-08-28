import datetime
from dataclasses import dataclass, asdict, field
from logging import Handler
from typing import List, Dict, Optional, Any

from ..notifiers.base import BaseNotifier


@dataclass
class TaskContext:
    task_id: str
    task_name: str
    func_name: str
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)

    notifier_config: List = field(default_factory=list)
    notifier_rules: Any = None
    notifiers: List[BaseNotifier] = field(default_factory=list)

    parent_task_id: Optional[str] = None
    max_retries: int = 0
    retry_delay: int = 0

    task_origin: str = "unk"
    allow_concurrent: bool = True
    task_type :str = 'unk'

    extra_context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    thread_handler: Optional[Handler] = None

    def to_dict(self):
        data = asdict(self)
        data["notifiers"] = [n.export_for_factory() if hasattr(n, "export_for_factory") else str(n) for n in self.notifiers]
        return data

    def log_context(self, key: Any = None, value: Any = None, **kwargs):
        #from domains.task_runner.notifiers.dispatch import dispatch_context

        # Case 1: called like log_context({"foo": "bar"})
        if isinstance(key, dict):
            for k, v in key.items():
                self.extra_context[k] = v
                #dispatch_context(self.task_id, k, v)
            return

        # Case 2: called like log_context("key", "value")
        if key is not None and value is not None:
            self.extra_context[key] = value
            #dispatch_context(self.task_id, key, value)

        # Case 3: called like log_context(foo="bar", count=1)
        for k, v in kwargs.items():
            self.extra_context[k] = v
            #dispatch_context(self.task_id, k, v)
