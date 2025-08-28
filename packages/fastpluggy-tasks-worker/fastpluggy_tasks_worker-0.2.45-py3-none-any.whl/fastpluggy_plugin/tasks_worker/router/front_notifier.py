# task_lock_router.py

from fastapi import APIRouter, Request, Depends

from fastpluggy.core.dependency import get_view_builder
from fastpluggy.core.view_builer.components.table import TableView
from fastpluggy.core.widgets import AutoLinkWidget
from fastpluggy.core.widgets.categories.input.button_list import ButtonListWidget
from ..notifiers.registry import get_notifier_registry

front_notifier_router = APIRouter(tags=["notifier"], prefix='/notifiers')


@front_notifier_router.get("/", name="view_notifier")
def view_notifier(request: Request, view_builder=Depends(get_view_builder)):
    registry = get_notifier_registry()
    data = registry.values()

    items = [
        ButtonListWidget(buttons=[
            AutoLinkWidget(label="Back to Task Dashboard", route_name="dashboard_tasks_worker"),
        ]),
        TableView(
            title="List of notifier",
            data=data,
            field_callbacks={
               # TaskLockDB.acquired_at: RenderFieldTools.render_datetime,
            },
            links=[
            ]
        )
    ]
    return view_builder.generate(request, widgets=items, title="Task Locks")
