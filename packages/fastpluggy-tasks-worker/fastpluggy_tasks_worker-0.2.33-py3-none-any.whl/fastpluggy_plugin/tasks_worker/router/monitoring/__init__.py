"""
Monitoring router package

This package centralizes operational endpoints intended for monitoring and observability.
It currently provides a placeholder FastAPI router and a migration plan (see plan.md)
for consolidating scattered monitoring-related endpoints into a single, well-structured
namespace.

Scope candidates to (re)host under `/monitoring` include:
- Health probes: readiness, liveness, and component-specific checks
- Metrics exposure: Prometheus scrape endpoints and app metrics
- System insights: CPU/memory/disk, GPU/CUDA info, process/thread pools
- Queue/task scheduler status (e.g., workers, schedules, retries, deadletter)
- Datastore insights: DB connectivity checks, Redis slowlog proxying, cache hit rates

Note: This module is intentionally not auto-registered. Integrators should explicitly
include `router` into the application once the migration plan is executed.
"""
from fastapi import APIRouter

from .schedule_monitoring import scheduled_tasks_monitoring_router
from .task_duration import monitoring_task_duration

# Placeholder router. Do not register automatically to avoid changing runtime behavior.
monitoring_router = APIRouter(prefix="/monitoring", tags=["monitoring"])
monitoring_router.include_router(scheduled_tasks_monitoring_router)
monitoring_router.include_router(monitoring_task_duration)