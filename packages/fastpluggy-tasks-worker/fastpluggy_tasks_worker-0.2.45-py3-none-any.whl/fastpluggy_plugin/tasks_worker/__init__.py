import contextvars
from typing import Optional, Dict, Any, Tuple

from fastpluggy.fastpluggy import FastPluggy
from .plugin import TaskRunnerPlugin
from .progress import task_progress

current_task_ctx = contextvars.ContextVar(
    "current_task_ctx", default=None
)

# task_context_var.py (continued)
from contextlib import contextmanager

@contextmanager
def set_current_task_ctx(ctx):
    token = current_task_ctx.set(ctx)
    try:
        yield
    finally:
        current_task_ctx.reset(token)

class TaskWorker:

    @staticmethod
    def submit(func,
               args: Optional[Tuple] = None,
               kwargs: Optional[dict] = None,
               task_name: Optional[str] = None,
               max_retries: int = 0,
               retry_delay: int = 0,
               parent_task_id: Optional[str] = None,
               task_origin: str = "unk",
               allow_concurrent: Optional[bool] = None,
               extra_context: Optional[dict] = None,
               ):
        ctx = current_task_ctx.get()
        if ctx:
            parent_task_id = ctx.task_id

        task_id = FastPluggy.get_global('tasks_worker').submit(
            func=func,
            args=args,
            kwargs=kwargs,
            task_name=task_name,
            max_retries=max_retries,
            retry_delay=retry_delay,
            parent_task_id=parent_task_id,
            task_origin=task_origin,
            allow_concurrent=allow_concurrent,
            extra_context=extra_context, )
        return task_id

    @staticmethod
    def set_task_progression(value: float, message: Optional[str] = None, meta: Optional[Dict[str, Any]] = None):
        """
        Update the current task's progress (0..100).
        Automatically resolves current task_id via ContextVar.
        """
        task_progress.update(value, message, meta)

#
#     @staticmethod
#     def add_scheduled_task(**kwargs):
#         pass
#
