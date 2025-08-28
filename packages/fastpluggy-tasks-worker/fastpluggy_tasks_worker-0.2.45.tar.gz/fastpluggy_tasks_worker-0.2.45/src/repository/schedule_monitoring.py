# controllers/scheduled_monitor_models.py

import re
from datetime import datetime, timezone  # ← only import what we use
from typing import Dict, List
from typing import Optional

from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field, model_validator, field_validator
from sqlalchemy import Text
from sqlalchemy import and_, select, cast
from sqlalchemy.orm import Session

from ..models.context import TaskContextDB
from ..models.report import TaskReportDB
from ..models.scheduled import ScheduledTaskDB


class FilterCriteria(BaseModel):
    """Container for filtering criteria - simplified to core filters only."""
    # Core filtering parameters
    task_name: Optional[str] = Field(None, description="Filter by task name (partial match)")
    start_time: Optional[datetime] = Field(None,description="Start time (ISO format or relative like '1h', '7d')")
    end_time: Optional[datetime] = Field(None, description="End time (ISO format or relative like '1h', '7d')")
    # Data limits
    max_reports_per_task: int = Field(10, ge=1, le=50, description="Max reports per task")

    # Pagination parameters
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(25, ge=1, le=100, description="Items per page")

    # Run BEFORE Pydantic’s own type coercion: str → datetime
    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def _parse_times(cls, v):
        try:
            return parse_single_time(v)
        except ValueError as e:
            # Pydantic will report this message back as a validation error
            raise ValueError(f"Invalid time for {cls.__name__}: {e}")

    # After all fields are set, enforce start ≤ end
    @model_validator(mode="after")
    def _check_time_order(self):
        if (
                self.start_time is not None
                and self.end_time is not None
                and self.start_time > self.end_time
        ):
            raise ValueError("start_time must be before or equal to end_time")
        return self

    def has_active_filters(self) -> bool:
        """Check if any filters are currently active."""
        return any([
            self.task_name,
            self.start_time,
            self.end_time,
        ])


def parse_single_time(time_str: Optional[str]) -> Optional[datetime]:
    """
    Parse time_str parameters supporting both ISO format and relative times.

    Supported formats:
      - ISO 8601: "2025-06-01T00:00:00Z" (and most other ISO‐ish variants)
      - Relative:   "1h" (1 hour ago), "7d" (7 days ago), "30m" (30 minutes ago), "45s" (45 seconds ago)
      - Special:    "now" (current UTC time)

    Returns:
      A datetime where each is either a datetime (naive, UTC)
      or `None` (if the corresponding input was `None` or empty).
    """
    RELATIVE_RE = re.compile(r"^(\d+)([smhd])$", re.IGNORECASE)

    if not time_str:
        return None

    s = time_str.strip().lower()

    # “now” shortcut
    if s == "now":
        return datetime.utcnow()

    # Try relative format, e.g. “15m”, “2h”, “7d”, “30s”
    m = RELATIVE_RE.match(s)
    if m:
        amount = int(m.group(1))
        unit = m.group(2)

        if unit == "s":
            delta = relativedelta(seconds=amount)
        elif unit == "m":
            delta = relativedelta(minutes=amount)
        elif unit == "h":
            delta = relativedelta(hours=amount)
        elif unit == "d":
            delta = relativedelta(days=amount)
        else:
            # (RegEx only allows s/m/h/d, so this branch should never happen)
            raise ValueError(f"Unknown relative‐time unit: '{unit}'")

        return datetime.utcnow() - delta

    # Otherwise, try to parse as ISO‐ish date/time
    try:
        # dateutil.parser.parse will accept “2025-06-01T00:00:00Z”, “2025-06-01 00:00:00”, “2025-06-01”, etc.
        dt = dateutil_parser.parse(time_str)
        # If the parsed datetime has timezone info, convert to naive UTC:
        if dt.tzinfo is not None:
            dt = dt.astimezone(tz=timezone.utc).replace(tzinfo=None)
        return dt
    except (ValueError, OverflowError) as e:
        raise ValueError(
            f"Invalid time format '{time_str}'.\n"
            f"Must be ISO (e.g. '2025-06-01T00:00:00Z'), ‘now’, or relative (e.g. '1h', '7d', '30m')."
        ) from e


def _fetch_scheduled_tasks(db: Session, criteria: FilterCriteria) -> List[ScheduledTaskDB]:
    """Fetch enabled scheduled tasks based on filtering criteria."""
    stmt = select(ScheduledTaskDB).where(ScheduledTaskDB.enabled == True)

    # Task name filter (partial match, case-insensitive)
    if criteria.task_name:
        stmt = stmt.where(ScheduledTaskDB.name.ilike(f"%{criteria.task_name}%"))

    stmt = stmt.order_by(ScheduledTaskDB.name)

    return db.execute(stmt).scalars().all()


def _fetch_reports_by_task(
        db: Session,
        scheduled_tasks: List[ScheduledTaskDB],
        max_per_task: int,
        criteria: FilterCriteria
) -> Dict[str, List[TaskReportDB]]:
    """
    For each ScheduledTaskDB.id in `scheduled_tasks`:
      1) Check if there’s a TaskContextDB row whose JSONB->>'schedule_id' equals that ID.
      2) If yes, fetch up to `max_per_task` TaskReportDB rows for that task (with time filters).
      3) Return a dict mapping EVERY requested task_id to a (possibly empty) list of reports.
    """

    if not scheduled_tasks:
        return {}

    # 1) Build a list of all the IDs (as strings) we care about:
    task_ids_str: List[str] = [str(task.id) for task in scheduled_tasks]

    # 2) Pre‐initialize the result so every task_id maps to an empty list:
    reports_by_task: Dict[str, List[TaskReportDB]] = {tid: [] for tid in task_ids_str}

    # 3) Prepare the JSONB expression once
    schedule_id_expr = TaskContextDB.extra_context["schedule_id"].astext

    # 4) For each schedule id in our original list:
    #      - If it appeared in matching_ids, run a small query to fetch up to max_per_task reports.
    #      - If not, leave its list as [].
    for tid in task_ids_str:
        #stmt_ctx = (
        #    select(TaskContextDB.task_id)
        #    .where(
        #        cast(schedule_id_expr, Text) == str(tid)
        #    )
        #)
        #matching_ids = set(db.execute(stmt_ctx).scalars().all())

        # Build a Query for this single task_id:
        rpt_stmt = select(TaskReportDB)#.where(TaskReportDB.task_id.in_(matching_ids))
        rpt_stmt = rpt_stmt.join(TaskContextDB, TaskReportDB.task_id == TaskContextDB.task_id).where(
            cast(schedule_id_expr, Text) == str(tid)
        )
        # Apply time filters if provided:
        time_conds = []
        if criteria.start_time:
            time_conds.append(TaskReportDB.start_time >= criteria.start_time)
        if criteria.end_time:
            time_conds.append(TaskReportDB.start_time <= criteria.end_time)
        if time_conds:
            rpt_stmt = rpt_stmt.where(and_(*time_conds))

        # Order descending and limit to max_per_task:
        rpt_stmt = rpt_stmt.order_by(TaskReportDB.start_time.desc()).limit(max_per_task)

        reports = db.execute(rpt_stmt).scalars().all()
        reports_by_task[tid] = reports

    return reports_by_task


def _build_filter_info(criteria: FilterCriteria, task_count: int) -> dict:
    """Build filter information for template display."""
    active_filters = []

    if criteria.task_name:
        active_filters.append(f"Name: '{criteria.task_name}'")

    if criteria.start_time:
        active_filters.append(f"Since: {criteria.start_time.strftime('%Y-%m-%d %H:%M')}")

    if criteria.end_time:
        active_filters.append(f"Until: {criteria.end_time.strftime('%Y-%m-%d %H:%M')}")

    return {
        "active_filters": active_filters,
        "has_filters": bool(active_filters),
        "task_count": task_count,
        "filter_summary": f"{len(active_filters)} active filter(s)" if active_filters else "No filters active"
    }


class TaskData(BaseModel):
    """
    Data model for a scheduled task with its execution history.
    All fields are populated during construction.
    """

    # Core task data
    id: int  # schedule_id
    last_task_id: Optional[str] = None  # last_task_id

    name: str
    description: str
    status: str
    schedule: str
    schedule_text: str

    # Execution data
    last_run: Optional[datetime]
    last_status: Optional[str]
    execution_time: str
    next_run: Optional[datetime]

    # Metrics
    uptime: float
    incidents: List[str]
    runs: List["ActivityData"]  # CHANGED: Now contains ActivityData objects instead of Any

    # UI helpers
    card_badge_color: str
    status_indicator_class: str

    @classmethod
    def from_db(cls, sched: ScheduledTaskDB, reports: List[TaskReportDB],  filter_criteria: FilterCriteria) -> "TaskData":
        """
        Constructor to create TaskData from SQLAlchemy objects.

        Args:
            sched: ScheduledTaskDB instance
            reports: List of TaskReportDB instances (sorted by start_time DESC)
        """
        # Basic info
        name = sched.name
        description = sched.function

        # Determine status
        if not sched.enabled:
            status = "maintenance"
        elif reports and reports[0].status == "failed":
            status = "issues"
        elif sched.is_late:
            status = "degraded"
        else:
            status = "operational"

        # Schedule info
        schedule = sched.cron or ""
        if sched.cron:
            schedule_text = sched.cron
        elif sched.interval:
            schedule_text = f"Every {sched.interval} seconds"
        else:
            schedule_text = "—"

        # Last execution info
        last_report = reports[0] if reports else None
        last_run = last_report.start_time if last_report else None
        last_status = last_report.status if last_report else None
        last_task_id = last_report.task_id if last_report else None

        # Calculate execution time
        if last_report and last_report.start_time and last_report.end_time:
            delta = last_report.end_time - last_report.start_time
            total_secs = int(delta.total_seconds())
            if total_secs >= 60:
                m, s = divmod(total_secs, 60)
                execution_time = f"{m}m {s}s"
            else:
                execution_time = f"{total_secs}s"
        elif last_report:
            # Handle different statuses
            if last_report.status == "failed":
                execution_time = "Failed"
            elif last_report.status == "running":
                execution_time = "Running..."
            elif last_report.status == "queued":
                execution_time = "Queued"
            else:
                execution_time = "N/A"
        else:
            execution_time = "N/A"

        # Next run
        next_run = sched.next_run

        # Calculate uptime percentage
        if reports:
            success_count = sum(1 for r in reports if r.status == "success")
            uptime = round((success_count / len(reports)) * 100.0, 1)
        else:
            uptime = 0.0

        # CHANGED: Build runs list with ActivityData objects instead of simple status strings
        runs = []
        # TODO: use filter here
        for report in reports[:filter_criteria.max_reports_per_task]:  # Limit to last 30 runs
            activity = ActivityData.from_report(report, name,  filter_criteria=filter_criteria)
            runs.append(activity)
            
        # Reverse the order of runs for the timeline display
        # This makes the timeline show oldest to newest (left to right)
        runs.reverse()

        # Pad to exactly 30 entries if needed (for UI consistency)
        # You might want to create "placeholder" ActivityData objects or handle this in the template

        # CHANGED: Build 30-day incidents list (keep this for backward compatibility if needed)
        incident_list = []
        for report in reports:
            incident_list.append("good" if report.status == "success" else "major")

        # Pad to exactly 30 entries with "good"
        if len(incident_list) < filter_criteria.max_reports_per_task:
            incident_list.extend(["good"] * (filter_criteria.max_reports_per_task - len(incident_list)))
        incidents = incident_list[:filter_criteria.max_reports_per_task]  # Ensure we don't exceed 30

        # UI helper mappings
        badge_colors = {
            "operational": "success",
            "issues": "danger",
            "degraded": "warning",
            "maintenance": "secondary"
        }

        indicator_classes = {
            "operational": "status-up",
            "issues": "status-down",
            "degraded": "status-warning",
            "maintenance": "status-maintenance"
        }

        card_badge_color = badge_colors.get(status, "primary")
        status_indicator_class = indicator_classes.get(status, "status-up")

        return cls(
            id=sched.id,
            last_task_id=last_task_id,
            name=name,
            description=description,
            status=status,
            schedule=schedule,
            schedule_text=schedule_text,
            last_run=last_run,
            last_status=last_status,
            execution_time=execution_time,
            next_run=next_run,
            uptime=uptime,
            incidents=incidents,  # Keep for backward compatibility
            runs=runs,  # CHANGED: Now contains ActivityData objects
            card_badge_color=card_badge_color,
            status_indicator_class=status_indicator_class,
        )


class ActivityData(BaseModel):
    """
    Activity timeline item for recent task executions.
    """
    timestamp: datetime
    type: str  # "success" | "warning" | "error"
    task: str
    task_name: Optional[str] = None
    task_id: str
    message: str

    @classmethod
    def from_report(cls, report: TaskReportDB, task_name: str, filter_criteria: FilterCriteria) -> "ActivityData":
        """
        Constructor to create ActivityData from a TaskReportDB.

        Args:
            report: TaskReportDB instance
            task_name: Human-readable task name
        """
        timestamp = report.start_time

        # Determine activity type and message based on report status
        if report.status == "success":
            activity_type = "success"
            message = "Task completed successfully"

            # Add execution time if available
            if report.end_time and report.start_time:
                duration = report.end_time - report.start_time
                total_secs = int(duration.total_seconds())
                if total_secs >= 60:
                    m, s = divmod(total_secs, 60)
                    message += f" in {m}m {s}s"
                else:
                    message += f" in {total_secs}s"

        elif report.status == "failed":
            activity_type = "error"
            error_info = report.error or {}

            if isinstance(error_info, dict) and error_info.get("message"):
                message = f"Task failed: {error_info['message']}"
            elif isinstance(error_info, str):
                message = f"Task failed: {error_info}"
            else:
                message = "Task failed with unknown error"

        elif report.status in ("queued", "running"):
            activity_type = "warning"
            message = f"Task {report.status.capitalize()}"

        else:
            activity_type = "error"
            message = f"Task status: {report.status or 'Unknown'}"

        return cls(
            timestamp=timestamp,
            type=activity_type,
            task=task_name,
            task_name=task_name,
            task_id=report.task_id,
            message=message,
        )


# class MonitorData(BaseModel):
#     """
#     Top‐level view model for the monitoring dashboard.
#     Contains all task data and recent activities with computed overall status.
#     """
#
#     # Core data
#     cron_tasks: List[TaskData]
#     activities: List[ActivityData]
#     last_update: str
#
#     # Overall status info
#     has_issues: bool
#     has_maintenance: bool
#     overall_uptime: str
#     overall_status_class: str
#     overall_title: str
#     overall_description: str
#     filter_criteria: FilterCriteria
#
#     @classmethod
#     def create(cls, scheduled_tasks: List[ScheduledTaskDB], reports_by_task: Dict[str, List[TaskReportDB]],
#                filter_criteria: FilterCriteria) -> "MonitorData":
#         """
#         Constructor to create MonitorData from database objects.
#
#         Args:
#             scheduled_tasks: List of ScheduledTaskDB instances
#             reports_by_task: Dict mapping schedule id (str) to List[TaskReportDB]
#             :param filter_criteria:
#         """
#         recent_activities = []
#         # Build TaskData instances
#         tasks_data = []
#         for sched in scheduled_tasks:
#             task_id_str = str(sched.id)
#             reports = reports_by_task.get(task_id_str, [])
#             task_data = TaskData.from_db(sched, reports, filter_criteria=filter_criteria)
#             tasks_data.append(task_data)
#             recent_activities.extend(reports)
#
#         # Create task name mapping from scheduled_tasks for activities
#         task_name_map = {task.id: task.name for task in scheduled_tasks}
#
#         # Build ActivityData instances
#         activities = []
#         for report in recent_activities:
#             try:
#                 task_name = task_name_map.get(report.task_id, f"Task {report.function} #{report.task_id}")
#             except (ValueError, TypeError):
#                 task_name = f"Task {report.function} #{report.task_id}"
#
#             activity = ActivityData.from_report(report, task_name, filter_criteria=filter_criteria)
#             activities.append(activity)
#
#         # Generate timestamp (DEPRECATED usage replaced here)
#         now_utc = datetime.now(timezone.utc)
#         last_update_str = now_utc.strftime("%b %d, %I:%M %p UTC")
#
#         # Calculate overall status
#         has_issues = any(t.status in ("issues", "degraded") for t in tasks_data)
#         has_maintenance = any(t.status == "maintenance" for t in tasks_data)
#
#         # Calculate overall uptime
#         if tasks_data:
#             total_uptime = sum(t.uptime for t in tasks_data)
#             avg_uptime = total_uptime / len(tasks_data)
#             overall_uptime = f"{avg_uptime:.2f}%"
#         else:
#             overall_uptime = "0.00%"
#
#         # Determine overall status
#         overall_status_class = "issues" if has_issues else "operational"
#
#         if has_issues:
#             overall_title = "Service Disruption"
#             overall_description = "Some tasks are experiencing issues"
#         elif has_maintenance:
#             overall_title = "Scheduled Maintenance"
#             overall_description = "Some tasks are under maintenance"
#         else:
#             overall_title = "All Systems Operational"
#             overall_description = "All cron tasks are running as expected"
#
#         return cls(
#             cron_tasks=tasks_data,
#             activities=activities,
#             last_update=last_update_str,
#             has_issues=has_issues,
#             has_maintenance=has_maintenance,
#             overall_uptime=overall_uptime,
#             overall_status_class=overall_status_class,
#             overall_title=overall_title,
#             overall_description=overall_description,
#             filter_criteria=filter_criteria,
#         )
