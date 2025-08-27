from collections import defaultdict

from fastapi import Request

from fastpluggy.core.widgets import AbstractWidget


class TaskFormView(AbstractWidget):
    widget_type = "task_form_view"

    template_name: str = "tasks_worker/task_form.html.j2"

    request: Request

    def __init__(
            self,
            title: str,
            submit_url: str,
            url_after_submit: str = None,
            tasks: list = None,
            mode: str = "create_task",
            url_list_available_tasks=None,
            url_list_available_notifiers=None,
            url_task_details=None,
            request: Request = None,

            **kwargs
    ):
        super().__init__(**kwargs)
        self.context = None
        self.title = title
        self.submit_url = submit_url
        self.url_after_submit = url_after_submit
        self.tasks = tasks or []
        self.mode = mode
        self.url_list_available_tasks = url_list_available_tasks
        self.url_list_available_notifiers = url_list_available_notifiers
        self.url_task_details = url_task_details
        self.request = request

    def process(self, **kwargs):
        self.url_list_available_tasks = self.url_list_available_tasks or self.request.url_for("list_available_tasks")
        self.url_list_available_notifiers = self.url_list_available_notifiers or self.request.url_for(
            "list_available_notifiers")
        self.url_task_details = self.url_task_details or self.request.url_for("task_details", task_id="TASK_ID_REPLACE")

        from ..task_registry import task_registry

        # Use passed tasks if available, otherwise load all from registry
        self.tasks = self.tasks or task_registry.list_metadata()
        self.has_tasks =  bool(self.tasks)

        tasks_by_package = defaultdict(list)
        for task in self.tasks:
            package = task.get("module", "unknown")
            tasks_by_package[package].append(task)
        self.tasks_by_package = dict(tasks_by_package)

        self.modal_title= self.title
