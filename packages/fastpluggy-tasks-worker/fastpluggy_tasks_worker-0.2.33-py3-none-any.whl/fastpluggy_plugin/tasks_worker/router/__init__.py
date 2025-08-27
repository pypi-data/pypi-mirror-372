from fastapi import APIRouter

from .api_notifier import api_notifier_router
from .api_registry import api_registry_router
from .api_tasks import api_tasks_router
from .debug import debug_router
from .front import front_task_router
from .front_lock import front_task_lock_router
from .front_notifier import front_notifier_router
from .front_schedule import front_schedule_task_router
from .metrics import metrics_router

# Global task queue registry

task_router = APIRouter(
    tags=["task_router"],
)

task_router.include_router(api_notifier_router)
task_router.include_router(api_registry_router)
task_router.include_router(api_tasks_router)
task_router.include_router(debug_router)
task_router.include_router(front_task_router)
task_router.include_router(front_task_lock_router)
task_router.include_router(front_notifier_router)
task_router.include_router(front_schedule_task_router)
task_router.include_router(metrics_router)

