# import logging
#
# from sqlalchemy.orm import Session
#
# from fastpluggy.core.database import get_db
# from ..models.report import TaskReportDB
# from ..notifiers.base import NotificationEvent
#
#
# def record_task_event(event: NotificationEvent):
#     db: Session = next(get_db())
#     try:
#         task = db.query(TaskReportDB).filter(TaskReportDB.task_id == event.task_id).first()
#         if task : #and event.success is not None:
#             logging.error(f"[DB HOOK ERROR] Task {event.task_id} already exists in DB")
#         #    task.status = TaskEvent.task_success if event.success else TaskEvent.task_failed
#         #    db.add(task)
#         from ..models.notification import TaskNotificationDB
#
#         db.add(TaskNotificationDB(
#             task_id=event.task_id,
#             event_type=event.event_type,
#             message=event.message,
#             timestamp=event.timestamp,
#         ))
#         db.commit()
#     except Exception as e:
#         logging.exception(f"[DB HOOK ERROR] Failed to save task event {event.task_id}: {e}")
#     finally:
#         db.close()
