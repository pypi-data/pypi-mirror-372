import inspect
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from fastapi import Request, Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastpluggy.core.database import get_db
from fastpluggy.core.dependency import get_fastpluggy
from fastpluggy.core.tools.inspect_tools import process_function_parameters
from fastpluggy.fastpluggy import FastPluggy
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..models.context import TaskContextDB
from ..models.report import TaskReportDB
from ..schema.request_input import CreateTaskRequest
from ..task_registry import task_registry

api_tasks_router = APIRouter(
    prefix='/api',
)


def get_task_context_and_repport(db: Session, task_id: str = None, limit: int = 20, filter_criteria=None):
    query = (
        db.query(TaskContextDB, TaskReportDB)
        .outerjoin(TaskReportDB, TaskContextDB.task_id == TaskReportDB.task_id)
    )

    if task_id:
        query = query.filter(TaskContextDB.task_id == task_id)
    else:
        # Apply filters if provided
        if filter_criteria:
            # Filter by task name if provided
            if filter_criteria.task_name:
                query = query.filter(TaskContextDB.task_name.ilike(f"%{filter_criteria.task_name}%"))
            
            # Filter by start time if provided
            if filter_criteria.start_time:
                query = query.filter(TaskReportDB.start_time >= filter_criteria.start_time)
            
            # Filter by end time if provided
            if filter_criteria.end_time:
                query = query.filter(TaskReportDB.start_time <= filter_criteria.end_time)
        
        query = query.order_by(desc(TaskContextDB.id)).limit(limit)

    rows = query.all()
    return rows


def get_task_context_reports_and_format(db: Session, task_id: str = None, limit: int = 20, filter_criteria=None):
    rows = get_task_context_and_repport(db=db, task_id=task_id, limit=limit, filter_criteria=filter_criteria)

    return [
        {
            "task_id": context.task_id,
            "task_name": context.task_name,
            "function": context.func_name,
            "args": context.args,
            "kwargs": context.kwargs,
            "notifier_config": context.notifier_config,
            "result": report.result if report else None,
            "logs": report.logs if report else None,
            "duration": report.duration if report else None,
            "error": report.error if report else None,
            "tracebacks": report.tracebacks if report else None,
            "attempts": report.attempts if report else None,
            "success": report.success if report else None,
            "status": report.status if report else None,
            "start_time": report.start_time.isoformat() if report and report.start_time else None,
            "end_time": report.end_time.isoformat() if report and report.end_time else None,
        }
        for context, report in rows
    ]


@api_tasks_router.get("/tasks", name="list_tasks")
async def list_tasks(
    db: Session = Depends(get_db),
    task_name: str = None,
    start_time: str = None,
    end_time: str = None
):
    from ..repository.schedule_monitoring import FilterCriteria
    
    # Create filter criteria with default date as today if not specified
    filter_criteria = FilterCriteria(
        task_name=task_name,
        start_time=start_time if start_time else "1d",  # Default to last 24 hours
        end_time=end_time if end_time else "now"        # Default to now
    )
    
    return get_task_context_reports_and_format(db, filter_criteria=filter_criteria)


@api_tasks_router.get("/task/{task_id}", name="get_task")
async def get_task(task_id: str, db: Session = Depends(get_db)):
    results = get_task_context_reports_and_format(db, task_id=task_id)
    if not results:
        return JSONResponse(status_code=404, content={"detail": "Task not found"})
    return results[0]


@api_tasks_router.post("/task/submit", name="submit_task")
async def submit_task(request: Request, payload: CreateTaskRequest ):
    runner = FastPluggy.get_global("tasks_worker")

    from ..task_registry import task_registry
    func = task_registry.get(payload.function)
    if not func:
        return JSONResponse({"error": "Function not found"}, status_code=400)

    sig = inspect.signature(func)
    input_kwargs = payload.kwargs
    typed_kwargs = process_function_parameters(func_signature=sig, param_values=input_kwargs)

    task_id = runner.submit(
        func,
        kwargs=typed_kwargs,
        task_name=payload.name or payload.function,
        notify_config=payload.notify_on,
        task_origin="api",
        max_retries=payload.max_retries,
        retry_delay=payload.retry_delay,
        allow_concurrent=payload.allow_concurrent,
    )

    return {"task_id": task_id}


@api_tasks_router.post("/task/{task_id}/retry", name="retry_task")
def retry_task(task_id: str, request: Request, db=Depends(lambda: next(get_db()))):
    context = db.query(TaskContextDB).filter(TaskContextDB.task_id == task_id).first()
    if not context:
        raise HTTPException(status_code=404, detail="Task context not found")

    func = task_registry.get(context.func_name)
    if not func:
        raise HTTPException(status_code=400, detail="Function not found in registry")

    task_name =f"{context.task_name} (retry)" if "(retry)" not in context.task_name else context.task_name
    # Re-submit the task with parent_task_id
    runner = FastPluggy.get_global("tasks_worker")
    new_task_id = runner.submit(
        func,
        args=context.args,
        kwargs=context.kwargs,
        task_name=task_name,
        parent_task_id=task_id,
        notify_config=context.notifier_config,
        task_origin="api-retry",
    )

    return {"task_id": new_task_id}



@api_tasks_router.post("/task/{task_id}/cancel", name="cancel_task")
async def cancel_task(task_id: str):
    """
    Cancel a running task by task_id and mark its status as 'manual_cancel'.
    """
    # Retrieve the global task runner instance.
    runner = FastPluggy.get_global("tasks_worker")
    if not runner:
        raise HTTPException(status_code=500, detail="Task runner is not available")

    # Attempt to cancel the running future.
    success = runner.cancel_task_with_notification(task_id)

    if not success:
        raise HTTPException(status_code=400, detail="Task not running or already finished")

    return {"task_id": task_id, "cancelled": success, "status": "manual_cancel"}


@api_tasks_router.get("/pool-info")
def get_thread_pool_info(fast_pluggy=Depends(get_fastpluggy)) -> dict:
    def get_pool_info(fast_pluggy: FastPluggy) -> dict[str, Any]:
        executor: ThreadPoolExecutor = fast_pluggy.executor
        runner = FastPluggy.get_global("tasks_worker")
        running_futures = runner.running_futures

        return {
            "max_workers": executor._max_workers,
            "currently_running": len([f for f in running_futures.values() if not f.done()]),
            "queued_tasks": len([f for f in running_futures.values() if not f.running() and not f.done()]),
            "total_tracked": len(running_futures),
        }

    return get_pool_info(fast_pluggy)
