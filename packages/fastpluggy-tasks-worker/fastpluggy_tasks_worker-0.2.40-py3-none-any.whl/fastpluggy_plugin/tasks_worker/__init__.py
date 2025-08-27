import contextvars
from typing import Optional, Dict, Any

#from .progress import progress
from .plugin import TaskRunnerPlugin

current_task_ctx = contextvars.ContextVar(
    "current_task_ctx", default=None
)

# class TaskWorker:
#
#     @staticmethod
#     def submit(self, **kwargs):
#         #
#         pass
#
#
#     @staticmethod
#     def set_task_progression(value: float, message: Optional[str] = None, meta: Optional[Dict[str, Any]] = None):
#         """
#         Update the current task's progress (0..100).
#         Automatically resolves current task_id via ContextVar.
#         """
#         progress.update(value, message, meta)
#
#
#     @staticmethod
#     def add_scheduled_task(**kwargs):
#         pass
#


# def on_message(msg):
#     token = current_task_ctx.set(TaskContext(task_id=msg.id, root_id=msg.root))
#     try:
#         execute_task(msg.name, *msg.args, **msg.kwargs)
#     finally:
#         current_task_ctx.reset(token)