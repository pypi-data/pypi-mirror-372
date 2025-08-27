from typing import Optional, List

from fastpluggy.core.config import BaseDatabaseSettings


class TasksRunnerSettings(BaseDatabaseSettings):

    # Thread pool settings
    thread_pool_max_workers: Optional[int] = None  # None means use default (CPU count * 5)

    # Scheduler
    scheduler_enabled: bool = True
    scheduler_frequency: float = 5
    allow_create_schedule_task: bool = True

    # notifier
    external_notification_loaders: Optional[List[str]] = []

    # Registry/Discover of tasks
    enable_auto_task_discovery: bool = True  # Enables scanning for task functions
    # Celery
    discover_celery_tasks: bool = True
    celery_app_path: str = "myproject.worker:celery_app"  # Path to the Celery app object
    discover_celery_schedule_enabled_status: bool = False # default status for enabled on creation of ScheduledTaskDB

    store_task_db: bool = True
    #store_task_notif_db: bool = False

    # Purge
    purge_enabled :bool = True
    purge_after_days: int = 30

# maybe add a module prefix
#    class Config:
#        env_prefix = "tasks_worker_"
    watchdog_enabled: bool = True
    #watchdog_frequency: float = 5
    watchdog_timeout_minutes: int = 120


