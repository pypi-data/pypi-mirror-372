from typing import Annotated

from fastapi import Depends, APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from starlette.requests import Request

from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_view_builder
from fastpluggy.core.widgets import CustomTemplateWidget
from ...models.report import TaskReportDB
from ...repository.schedule_monitoring import FilterCriteria

monitoring_task_duration = APIRouter(
    tags=["task_router"],
)


@monitoring_task_duration.get("/task_duration", response_class=HTMLResponse, name="task_duration_analytics")
async def task_duration_analytics(request: Request, view_builder=Depends(get_view_builder), ):
    # Generate the URL for the task-reports API endpoint using url_for
    api_task_reports_url = request.url_for("get_task_reports")

    items = [
        CustomTemplateWidget(
            template_name='tasks_worker/monitoring/task_time.html.j2',
            context={
                "request": request,
                "api_task_reports_url": api_task_reports_url,
            }
        ),
    ]

    return view_builder.generate(
        request,
        title="Task Duration Analytics",
        widgets=items
    )


@monitoring_task_duration.post("/task_duration/data")
async def get_task_reports(      request: Request,
        filter_criteria: Annotated[FilterCriteria, Query()],
        db: Session = Depends(get_db),
        view_builder=Depends(get_view_builder),):
    try:
        # Apply filters to your SQLAlchemy query
        query = db.query(TaskReportDB)

        if filter_criteria.task_name:
            query = query.filter(TaskReportDB.function.ilike(f"%{filter_criteria.task_name}%"))

        if filter_criteria.start_time:
            query = query.filter(TaskReportDB.start_time >= filter_criteria.start_time)

        if filter_criteria.end_time:
            query = query.filter(TaskReportDB.end_time <= filter_criteria.end_time)

        # Limit results per task
        # You might need custom logic here depending on your requirements

        results = query.all()

        # Return in expected format
        return [
            {
                "id": task.id,
                "function": task.function,
                "duration": task.duration,
                "status": task.status,
                "start_time": task.start_time.isoformat(),
                "end_time": task.end_time.isoformat() if task.end_time else None
            }
            for task in results
        ]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
