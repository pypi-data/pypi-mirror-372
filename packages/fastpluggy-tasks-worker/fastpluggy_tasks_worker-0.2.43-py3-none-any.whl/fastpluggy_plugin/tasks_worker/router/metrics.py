from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import psutil
from typing import Optional, Dict

from fastpluggy.core.database import get_db

from ..models.report import TaskReportDB

metrics_router = APIRouter()


def get_task_metrics(pid: int) -> Optional[Dict]:
    try:
        p = psutil.Process(pid)
        return {
            "pid": pid,
            "cpu_percent": p.cpu_percent(interval=0.1),  # small interval to get current usage
            "memory_info": {
                "rss": p.memory_info().rss,  # Resident Set Size
                "vms": p.memory_info().vms,  # Virtual Memory Size
            },
            "create_time": p.create_time(),
            "status": p.status(),
            "num_threads": p.num_threads(),
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


@metrics_router.get("/tasks/{task_id}/metrics")
def get_task_resource_usage(task_id: str, db: Session = Depends(get_db)):
    task : TaskReportDB = db.query(TaskReportDB).filter(TaskReportDB.task_id == task_id).first()
    if not task or not task.thread_native_id:
        return {"error": "Task not found or PID missing"}

    metrics = get_task_metrics(int(task.thread_ident))
    return metrics or {"error": "Process not running or inaccessible"}
