from fastapi import APIRouter, Request, Depends

from fastpluggy.core.auth import require_authentication
from fastpluggy.core.dependency import get_view_builder
from fastpluggy.core.widgets.categories.data.debug import DebugView
from ..config import TasksRunnerSettings
from ..services.task_discovery import discover_celery_periodic_tasks
from ..services.task_discovery import discover_celery_tasks_from_app

# Set custom /proc path if provided
# custom_proc_path = os.getenv("PROCFS_PATH", "/proc")

debug_router = APIRouter(
    prefix="/debug",
    tags=["debug"],
    dependencies=[Depends(require_authentication)],
)

#
# @debug_router.get("/", name="list_threads")
# async def list_threads(
#         request: Request,
#         db: Session = Depends(get_db),
#         view_builder=Depends(get_view_builder)
# ):
#     # if host_proces:
#     #    psutil.PROCFS_PATH = custom_proc_path
#
#     process = psutil.Process()
#     num_threads = process.num_threads()
#     process_dict = process.as_dict()
#     threads = process_dict['threads']
#     threads_dict = [item._asdict() for item in threads]
#     clean_threads_dict = threads_dict
#     #clean_threads_dict = get_list_task_by_pid(db, threads_dict)
#
#     threads_enum = [thread for thread in threading.enumerate()]
#
#     return view_builder.generate(
#         request,
#         title=f"Thread list (running {num_threads})",
#         items=[
#             ButtonListWidget(buttons=[
#                 AutoLinkWidget(route_name="celery_list_tasks"),
#             ]),
#             TableView(
#                 data=clean_threads_dict,
#                 field_callbacks={'status': RenderFieldTools.render_enum},
#                 links=[
#                     AutoLinkWidget(
#                         label="Details", route_name="task_details",
#                         #param_mapping={'task_id': 'task_id'},
#                         condition=lambda task: task['task_id'] is not None),
#                 ]
#             ),
#             TabbedWidget(tabs=[
#                 DebugView(data=threads_enum, title="Thread Enum"),
#                 DebugView(data=clean_threads_dict, title="Clean threads dict"),
#                 DebugView(data=process_dict, title="Process"),
#                 DebugView(data=threads_dict, title="Thread"),
#             ]),
#             ButtonListWidget(buttons=[
#                 AutoLinkWidget(label="Back to Task Dashboard", route_name="dashboard_tasks_worker"),
#             ]),
#         ]
#     )

@debug_router.get("/celery_list_tasks", name="celery_list_tasks")
async def celery_list_tasks(
        request: Request,
        view_builder=Depends(get_view_builder)
):
    settings = TasksRunnerSettings()
    data = discover_celery_tasks_from_app(settings.celery_app_path)
    schedule = discover_celery_periodic_tasks(settings.celery_app_path)

    return view_builder.generate(
        request,
        title="Celery list",
        items=[
            DebugView(data=data, title="Celery Tasks"),
            DebugView(data=schedule, title="Celery Scheduled Tasks"),
        ]
    )

