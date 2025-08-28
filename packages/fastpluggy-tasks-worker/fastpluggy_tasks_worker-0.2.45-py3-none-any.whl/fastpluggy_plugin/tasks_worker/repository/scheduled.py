import json
import logging
from typing import Optional, Callable

from ..models.scheduled import ScheduledTaskDB


def ensure_scheduled_task_exists(
        db,
        function: Callable | str,
        task_name: Optional[str] = None,
        cron: Optional[str] = None,
        interval: Optional[int] = None,
        kwargs: Optional[dict] = None,
        notify_config: Optional[dict] = None,
        max_retries: int = 0,
        retry_delay: int = 0,
enabled:bool=False,
):
    """
    # TODO: maybe use CreateScheduledTaskRequest like in endpoint for consistency
    Ensure a ScheduledTaskDB entry exists for the given function and cron.
    If not, create it.
    `function` can be a callable or a string.
    `task_name` is used to check uniqueness.
    """
    if task_name is None:
        task_name = function.__name__ if callable(function) else function

    # Use task_name directly in filter (already a str)
    existing = db.query(ScheduledTaskDB).filter_by(name=task_name).first()

    if not existing:
        function_name = function.__name__ if callable(function) else function
        scheduled = ScheduledTaskDB(
            name=task_name,
            cron=cron,
            interval=interval,
            function=function_name,
            kwargs=json.dumps(kwargs or {}),
            notify_on=json.dumps(notify_config or {}),
            # max_retries=max_retries,
            # retry_delay=retry_delay,
            enabled=enabled,
        )
        db.add(scheduled)
        db.commit()
        logging.info(f"[SCHEDULER] Created new ScheduledTaskDB entry for '{task_name}'")
