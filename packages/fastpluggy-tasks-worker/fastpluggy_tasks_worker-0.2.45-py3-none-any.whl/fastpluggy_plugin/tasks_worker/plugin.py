# plugin.py
import logging
from typing import Annotated, Any

from fastpluggy.core.database import session_scope, create_table_if_not_exist
from fastpluggy.core.menu.schema import MenuItem
from fastpluggy.core.module_base import FastPluggyBaseModule
from fastpluggy.core.plugin_state import PluginState
from fastpluggy.core.tools.inspect_tools import InjectDependency
from fastpluggy.core.tools.install import is_installed

from .config import TasksRunnerSettings


def get_task_router():
    from .router import task_router
    from .router.monitoring import monitoring_router

    return [
        task_router,
        monitoring_router
    ]


class TaskRunnerPlugin(FastPluggyBaseModule):
    module_name: str = "tasks_worker"

    module_menu_name: str = "Task Runner"
    module_menu_type: str = "main"

    module_settings: Any = TasksRunnerSettings
    module_router: Any = get_task_router

    extra_js_files: list = []

    depends_on: dict = {
        "crud_tools": ">=0.0.2",
    }

    optional_dependencies: dict = {
        "websocket_tool": ">=0.1.0",
        "ui_tools": ">=0.0.2",
    }
    
    def after_setup_templates(self, fast_pluggy: Annotated["FastPluggy", InjectDependency]) -> None:
        """
        Add global Jinja template variable for the API URL to trigger tasks.
        """
        # Add URL for task submission endpoint to global Jinja templates
        fast_pluggy.templates.env.globals["task_submit_url"] = fast_pluggy.app.url_path_for("submit_task")

    def on_load_complete(
            self,
            fast_pluggy: Annotated["FastPluggy", InjectDependency],
            plugin: Annotated["PluginState", InjectDependency],
    ) -> None:

        settings: TasksRunnerSettings = TasksRunnerSettings()

        from .models.scheduled import ScheduledTaskDB
        create_table_if_not_exist(ScheduledTaskDB)

        if settings.store_task_db:
            from .models.context import TaskContextDB
            create_table_if_not_exist(TaskContextDB)
            from .models.report import TaskReportDB
            create_table_if_not_exist(TaskReportDB)

            # if settings.store_task_notif_db:
            #    from .models.notification import TaskNotificationDB
            #    create_table_if_not_exist(TaskNotificationDB)

        # Add UI menu entries
        fast_pluggy.menu_manager.add_parent_item(
            menu_type='main',
            item=MenuItem(label="Task Runner", icon="fa-solid fa-gears", parent_name=self.module_name)
        )

        # Discover tasks
        from .services.task_discovery import discover_tasks_from_loaded_modules, discover_celery_tasks_from_app

        if settings.enable_auto_task_discovery:
            discover_tasks_from_loaded_modules(fast_pluggy=fast_pluggy)

        if settings.discover_celery_tasks:
            from .services.task_discovery import discover_celery_periodic_tasks

            if ':' in settings.celery_app_path:
                if is_installed("celery"):
                    discover_celery_tasks_from_app(settings.celery_app_path, plugin_state=plugin)
                    discover_celery_periodic_tasks(settings.celery_app_path, plugin_state=plugin)
                else:
                    logging.warning("Celery is NOT installed.")
            else:
                logging.warning(f"Celery app path '{settings.celery_app_path}' is not a valid path. ")

        # check if a worker alrady exist
        old_runner = fast_pluggy.get_global('tasks_worker')
        if old_runner is not None:
            logging.warning("A worker already exist. Shutting down old runner.")
            old_runner.graceful_shutdown()

        # Register global runner
        from .runner import TaskRunner
        runner = TaskRunner(fast_pluggy=fast_pluggy)
        fast_pluggy.register_global('tasks_worker', runner)

        # Register default notifiers
        from .notifiers.registry import setup_default_notifiers
        from .notifiers.loader import load_external_notification_config_from_settings

        setup_default_notifiers()
        load_external_notification_config_from_settings()

        # Launch scheduler in background
        if settings.scheduler_enabled:
                from .tasks.scheduler import schedule_loop
                runner.submit(
                    schedule_loop,
                    task_name="Scheduler",
                    allow_concurrent=False,
                    max_retries=-1
                )

        # Setup scheduled maintenance tasks
        if settings.store_task_db:
            with session_scope() as db:
                from .repository.scheduled import ensure_scheduled_task_exists

                if settings.purge_enabled:
                    from .tasks.maintenance import purge_old_tasks
                    ensure_scheduled_task_exists(
                        db=db,
                        function=purge_old_tasks,
                        task_name="purge_old_tasks",
                        cron="0 4 * * *",  # Every day at 4am
                    )

                # if settings.watchdog_enabled:
                # todo : move to worker class to ensure all is always sync
                #    from .tasks.watchdog import watchdog_cleanup_stuck_tasks
                #    ensure_scheduled_task_exists(
                #        db=db,
                #        function=watchdog_cleanup_stuck_tasks,
                #        task_name="watchdog_cleanup_stuck_tasks",
                #        interval=15,  # Every 15 minutes
                #    )

