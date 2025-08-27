from typing import Optional


from fastpluggy.core.database import session_scope
from fastpluggy.core.tools.serialize_tools import serialize_value
from ..models.context import TaskContextDB
from ..schema.status import TaskStatus
from ..models.report import TaskReportDB
from ..schema.context import TaskContext


def save_context(context: TaskContext) -> None:
    """
    Persist a TaskContext to the database.
    """

    data = serialize_value(context.to_dict())

    with session_scope() as db:
        data = TaskContextDB(**data)
        db.add(data)
        db.commit()


# def record_skipped_task(context: TaskContext, report: TaskReport) -> None:
#     """
#     Persist both the TaskContext and a skipped TaskReport.
#     """
#     db: Session = next(get_db())
#     try:
#         db.add(context.to_db_model())
#         db.add(report.to_db_model())
#         db.commit()
#     finally:
#         db.close()


def cancel_report(task_id: str) -> Optional[TaskContextDB]:
    """
    Mark an existing TaskReport as manually cancelled and return its TaskContextDB.
    """

    with session_scope() as db:
        report = db.query(TaskReportDB).filter(TaskReportDB.task_id == task_id).first()
        if report:
            report.status = TaskStatus.MANUAL_CANCELLED
            db.commit()
        context = db.query(TaskContextDB).filter(TaskContextDB.task_id == task_id).first()
        return context

