import datetime
from dataclasses import dataclass, asdict, field
from logging import Handler
from typing import List, Dict, Optional, Any

from ..notifiers.base import BaseNotifier


@dataclass
class TaskContext:
   # notifiers: Optional[List[BaseNotifier]] = None

    #extra_context: dict[str, Any] = {}
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

    extra_context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    thread_handler: Optional[Handler] = None

# def __init__(
    #         self,

    #         task_name: str,
    #         func_name: str,
    #         args: List[Any],
    #         kwargs: Dict[str, Any],
    #         notify_config: Optional[Dict[str, List[str]]] = None,
    #         thread_handler: Optional[Handler] = None,
    #         parent_task_id: Optional[str] = None,
    #         max_retries: int = 0,
    #         retry_delay: int = 0,
    #         notifiers: Optional[List[BaseNotifier]] = None,
    #         resolved_notifier_rules=None,
    #         task_origin: str = "unk",  # Add here
    #         allow_concurrent: bool = True
    # ):
    #     self.task_id = task_id
    #     self.parent_task_id = parent_task_id
    #     self.task_name = task_name
    #     self.func_name = func_name
    #     self.args = args
    #     self.kwargs = kwargs
    #     self.notify_config = notify_config or []
    #     self.resolved_notifier_rules = resolved_notifier_rules
    #     self.thread_handler = thread_handler
    #     self.max_retries = max_retries
    #     self.retry_delay = retry_delay
    #     self.notifiers = notifiers or []
    #     self.task_origin = task_origin
    #     self.allow_concurrent = allow_concurrent
    #     self.created_at = datetime.datetime.now(datetime.UTC)

    def to_dict(self):
        data = asdict(self)
        data["notifiers"] = [n.export_for_factory() if hasattr(n, "export_for_factory") else str(n) for n in self.notifiers]
        return data


   # def to_db_model(self) -> TaskContextDB:
   #     return TaskContextDB(
          #  task_id=self.task_id,
          #  parent_task_id=self.parent_task_id,
        #    task_name=self.task_name,
        #    function=self.func_name,
        #    args=json.dumps([str(x) for x in self.args]),
        #    kwargs=json.dumps({k: str(v) for k, v in self.kwargs.items()}),
        #    notify_config=json.dumps(self.notify_config),
      #      resolved_notifiers=self.serialized_notifier(),
    #        max_retries=self.max_retries,
    #        retry_delay=self.retry_delay,
#            created_at=datetime.utcnow(),
   #         task_origin=self.task_origin,
   #         allow_concurrent=self.allow_concurrent,
    #    )

  #  def serialized_notifier(self):
  #      return json.dumps([ i.export_for_factory() for i in self.notifiers ])

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
