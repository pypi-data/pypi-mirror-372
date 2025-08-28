import datetime

from fastpluggy.core.database import session_scope
from fastpluggy.core.tools.serialize_tools import serialize_value
from fastpluggy.core.tools.threads_tools import get_tid, get_py_ident
from ..models.report import TaskReportDB
from ..schema.report import TaskReport
from ..schema.status import TaskStatus


def init_report_from_context(context: "TaskContext") -> TaskReport:
    """
    Create and persist an initial TaskReport based on the context.
    """
    report = TaskReport(
        task_id=context.task_id,
        function=context.func_name,
        args=[str(a) for a in context.args],
        kwargs={k: str(v) for k, v in context.kwargs.items()},
        start_time=datetime.datetime.now(datetime.UTC),
        status=TaskStatus.RUNNING,
        thread_native_id=get_tid(),
        thread_ident=get_py_ident(),
    )
    return report


def save_report(report: TaskReport) -> None:
    """
    Persist the initial TaskReport before execution.
    """
    with session_scope() as db:
        data = TaskReportDB(**report.to_dict())
        db.add(data)
        db.commit()


def update_report(report: TaskReport) -> None:
    """
    Update fields on an existing TaskReportDB and in-memory TaskReport.
    """

    with session_scope() as db:
        exists = db.query(TaskReportDB).filter(TaskReportDB.task_id == report.task_id).first()
        if not exists:
            return

        data = report.to_dict()

        if 'result' in data:
            data['result'] = str(serialize_value(data['result']))

        # Update fields from data
        for key, value in data.items():
            if hasattr(exists, key):
                setattr(exists, key, value)

        db.add(exists)
        db.commit()
        db.refresh(exists)
        return exists
