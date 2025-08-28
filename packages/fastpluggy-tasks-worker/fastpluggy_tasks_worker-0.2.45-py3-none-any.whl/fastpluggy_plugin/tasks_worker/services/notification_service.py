from datetime import datetime
from typing import Optional

from ..config import TasksRunnerSettings
from ..notifiers.base import NotificationEvent
from ..notifiers.registry import dispatch_notification
#from ..repository.task_events import record_task_event
from ..schema.context import TaskContext
from ..schema.report import TaskReport
from ..schema.status import TaskStatus
from ..schema.task_event import TaskEvent


class TaskNotificationService:
    @staticmethod
    def build_event(
            event_type: TaskStatus,
            context: TaskContext,
            report: Optional[TaskReport] = None,
            message: Optional[str] = None,
            percent: Optional[float] = None,
            step: Optional[str] = None,
    ) -> NotificationEvent:
        timestamp = report.end_time if report and report.end_time else datetime.utcnow()
        task_id = context.task_id
        name = context.task_name
        function = report.function if report else context.func_name

        # Auto-generate message if not provided
        if not message:
            if event_type == TaskEvent.task_started:
                message = f"Task `{name}` started."
            elif event_type == TaskEvent.task_success:
                message = f"Task `{function}` success after {report.attempts} attempt(s)."
            elif event_type == TaskEvent.task_failed:
                message = f"Task `{function}` failed after {report.attempts} attempt(s)."
            elif event_type == TaskEvent.task_progress:
                message = f"Task `{name}` progress update."
                if step:
                    message += f" Step: {step}"
                if percent is not None:
                    message += f" ({percent:.0f}%)"

        return NotificationEvent(
            event_type=event_type,
            task_id=task_id,
            name=name,
            function=function,
            timestamp=timestamp,
            message=message,
            success=report.success if report else None,
            error=report.error if report else None,
            # TODO : fix missng info
            # percent=percent,
            # step=step,
        )

    @staticmethod
    def notify_task_status(report: TaskReport, context: TaskContext):
        event = TaskNotificationService.build_event(event_type=report.status, context=context, report=report)
        settings = TasksRunnerSettings()
        #if settings.store_task_notif_db:
        #    record_task_event(event=event)
        dispatch_notification(event, context=context)

    # @staticmethod
    # def notify_start(context: TaskContext):
    #     event = TaskNotificationService.build_event(TaskEvent.task_started, context)
    #     record_task_event(event=event)
    #     dispatch_notification(event, context=context)
    #
    # @staticmethod
    # def notify_task_end(report: TaskReport, context: TaskContext):
    #     #event_type = TaskEvent.task_success if report.success else TaskEvent.task_failed
    #     event_type = report.status
    #     event = TaskNotificationService.build_event(event_type, context, report)
    #     record_task_event(event=event)
    #     dispatch_notification(event, context=context)

    # @staticmethod
    # def notify_manual_cancel(report: TaskReport, context: TaskContext):
    #     """
    #     Notify that a task was manually cancelled.
    #     """
    #     # Create a manual cancellation event using the new event type.
    #     event = TaskNotificationService.build_event(TaskEvent.task_cancelled, context, report)
    #     record_task_event(event=event)
    #     dispatch_notification(event, context=context)

    @staticmethod
    def notify_progress(
            context: TaskContext,
            message: str,
            percent: Optional[float] = None,
            step: Optional[str] = None,
    ):
        event = TaskNotificationService.build_event(
            TaskEvent.task_progress,
            context,
            message=message,
            percent=percent,
            step=step,
        )
        settings = TasksRunnerSettings()
        #if settings.store_task_notif_db:
        #    record_task_event(event=event)
        dispatch_notification(event, context=context)

    @staticmethod
    def cleanup_notifiers(context: TaskContext):
        for notifier in context.notifiers:
            try:
                notifier.on_task_done(context.task_id)
            except Exception as e:
                print(f"[NOTIFIER CLEANUP ERROR] {notifier.name}: {e}")
