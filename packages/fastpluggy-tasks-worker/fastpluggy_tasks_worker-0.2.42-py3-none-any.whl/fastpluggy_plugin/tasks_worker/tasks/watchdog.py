from datetime import datetime, timedelta, timezone
from sqlalchemy import select

from ..config import TasksRunnerSettings
from ..models.report import TaskReportDB
from fastpluggy.core.database import session_scope
from ..schema.status import TaskStatus

from ..task_registry import task_registry


@task_registry.register(name="watchdog.cleanup_stuck_tasks")
async def watchdog_cleanup_stuck_tasks():
    settings = TasksRunnerSettings()

    timeout_minutes = settings.watchdog_timeout_minutes
    threshold = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)

    with session_scope() as session:
        result = session.execute(
            select(TaskReportDB)
            .where(TaskReportDB.finished == False)
            .where(TaskReportDB.start_time < threshold)
        )
        stuck_tasks = result.scalars().all()

        count = 0

        for task in stuck_tasks:
            # todo: check if task is running
            is_running = True
            if not is_running:

                task.status = TaskStatus.TIMEOUT
                task.finished = True
                task.finished_at = datetime.now(timezone.utc)
                task.result = "Watchdog timeout — task did not finish in time"
                count += 1

                # TODO : remove the task_lock if pid is not running anymore
                #  -> maybe use notification system
                # await notify_task_event(
                #     event=TaskEvent.STATUS,
                #     task_id=task.task_id,
                #     status="timeout",
                #     message="Task marked as timed out by watchdog",
                # )

        session.commit()

    return f"{count} tasks marked as timeout by watchdog."
