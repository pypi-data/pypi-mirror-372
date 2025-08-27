import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
from fastpluggy.core.database import get_db
from ..models.context import TaskContextDB
from ..models.report import TaskReportDB
#from ..models.notification import TaskNotificationDB
from ..config import TasksRunnerSettings
from ..schema.status import TaskStatus
from ..task_registry import task_registry



def purge_old_tasks_db(db: Session, older_than_days: int):
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    statuses = [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELLED]

    # Retrieve all the report records older than the cutoff and matching the specified statuses.
    reports = db.query(TaskReportDB).filter(
        TaskReportDB.end_time < cutoff, TaskReportDB.status.in_(statuses)
    ).all()
    task_ids = [r.task_id for r in reports]

    total_notifications_deleted = 0
    total_contexts_deleted = 0
    total_reports_deleted = 0

    # Iterate over each task_id and delete related rows.
    for task_id in task_ids:
        # TODO : purge the NotificationRecordDB
        #notif_deleted = db.query(TaskNotificationDB).filter(
        #    TaskNotificationDB.task_id == task_id
        #).delete(synchronize_session=False)

        ctx_deleted = db.query(TaskContextDB).filter(
            TaskContextDB.task_id == task_id
        ).delete(synchronize_session=False)
        rep_deleted = db.query(TaskReportDB).filter(
            TaskReportDB.task_id == task_id
        ).delete(synchronize_session=False)

        # Log the number of rows deleted for this task_id.
        logging.info(
           # f"Task {task_id}: Deleted {notif_deleted} notifications, "
            f"{ctx_deleted} contexts, and {rep_deleted} reports."
        )

        #total_notifications_deleted += notif_deleted
        total_contexts_deleted += ctx_deleted
        total_reports_deleted += rep_deleted

    db.commit()

    # Log the aggregated totals.
    logging.info(
        f"Purged tasks for {len(task_ids)} task IDs. Total rows deleted: "
        f"Notifications: {total_notifications_deleted}, "
        f"Contexts: {total_contexts_deleted}, "
        f"Reports: {total_reports_deleted}."
    )

    return {
        "purged_task_ids": task_ids,
        "deleted_notification": total_notifications_deleted,
        "deleted_context": total_contexts_deleted,
        "deleted_report": total_reports_deleted,
    }


@task_registry.register(
    name="purge_old_tasks",
    description="Purge old tasks based on retention period",
)
def purge_old_tasks():
    db = next(get_db())
    settings = TasksRunnerSettings()
    return purge_old_tasks_db(db, settings.purge_after_days)
