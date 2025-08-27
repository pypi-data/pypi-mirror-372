import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_view_builder
from fastpluggy.core.menu.decorator import menu_entry
from fastpluggy.core.widgets import CustomTemplateWidget
from ...models.scheduled import ScheduledTaskDB
from ...repository.schedule_monitoring import (
    _build_filter_info,
    _fetch_reports_by_task,
    _fetch_scheduled_tasks,
    FilterCriteria,
    TaskData,
)

scheduled_tasks_monitoring_router = APIRouter(
    prefix="/scheduled_task",
    tags=["task_router"],
)


@menu_entry(label="Schedule Monitoring", icon='ti ti-activity')
@scheduled_tasks_monitoring_router.get("", name="scheduled_task_monitoring")
async def scheduled_task_monitoring(
        request: Request,
        filter_criteria: Annotated[FilterCriteria, Query()],
        db: Session = Depends(get_db),
        view_builder=Depends(get_view_builder),
):
    """
    Async version of the Cron Task Status Monitor page.
    Keeps the same path and behavior, preparing the template context.
    """
    # Enforce safe bounds on filter/pagination inputs
    filter_criteria.max_reports_per_task = min(max(1, filter_criteria.max_reports_per_task), 50)

    # Fetch all scheduled tasks (for counting + pagination)
    all_scheduled_tasks = _fetch_scheduled_tasks(db, filter_criteria)

    total_tasks = len(all_scheduled_tasks)
    total_pages = (total_tasks + filter_criteria.page_size - 1) // filter_criteria.page_size

    filter_info = _build_filter_info(filter_criteria, total_tasks)

    pagination_info = {
        "current_page": filter_criteria.page,
        "total_pages": total_pages,
        "page_size": filter_criteria.page_size,
        "total_items": total_tasks,
        "has_previous": filter_criteria.page > 1,
        "has_next": filter_criteria.page < total_pages,
        "previous_page": filter_criteria.page - 1 if filter_criteria.page > 1 else None,
        "next_page": filter_criteria.page + 1 if filter_criteria.page < total_pages else None,
    }

    return view_builder.generate(
        request,
        widgets=[CustomTemplateWidget(
            template_name="tasks_worker/monitoring/scheduled_monitor.html.j2",
            context={
                "scheduled_tasks": all_scheduled_tasks,
                "filter_criteria": filter_criteria,
                "filter_info": filter_info,
                "pagination": pagination_info,
                "url_retry_task": str(request.url_for("retry_task", task_id="TASK_ID_REPLACE")),
                "url_task_details": str(request.url_for("task_details", task_id="TASK_ID_REPLACE")),
                "url_task_detail_data": str(
                    request.url_for("scheduled_task_detail_data", schedule_id="SCHED_ID_REPLACE")),
                "current_params": filter_criteria,
            },
        )],
    )


@scheduled_tasks_monitoring_router.get("/task/{schedule_id}/data", name="scheduled_task_detail_data")
async def scheduled_task_detail_data(
        schedule_id: int,
        request: Request,
        filter_criteria: Annotated[FilterCriteria, Query()],
        db: Session = Depends(get_db),
):
    try:
        # clamp inputs
        filter_criteria.max_reports_per_task = min(max(1, filter_criteria.max_reports_per_task), 50)
        # Fetch the scheduled task
        sched = db.query(ScheduledTaskDB).filter(ScheduledTaskDB.id == schedule_id).first()
        if not sched:
            return JSONResponse(status_code=404, content={"error": "Scheduled task not found"})

        reports_by_task = _fetch_reports_by_task(db, [sched], filter_criteria.max_reports_per_task, filter_criteria)
        reports = reports_by_task.get(str(sched.id), [])
        task_data = TaskData.from_db(sched, reports, filter_criteria)
        return task_data
    except Exception as e:
        logging.error(f"Error in scheduled_task_detail_data: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": str(e)})