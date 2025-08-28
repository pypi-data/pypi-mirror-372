from fastapi import APIRouter

api_registry_router = APIRouter(
    prefix='/api/registry',
)


@api_registry_router.get("/available", name="list_available_tasks")
def list_available_tasks():
    from ..task_registry import task_registry
    meta = task_registry.list_metadata()
    return meta

