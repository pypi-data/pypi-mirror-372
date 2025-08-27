from typing import Optional, Dict, Any

from fastpluggy.core.widgets import BaseButtonWidget, RequestParamsMixin


class RunTaskButtonWidget(BaseButtonWidget, RequestParamsMixin):
    """
    Simple button widget with URL navigation.
    """

    widget_type = "button"


    def __init__(self, task: str, task_kwargs, **kwargs):
        """
        Initialize button widget.

        Args:
            url: Target URL (supports placeholders like <field_name>)
        """
        super().__init__(**kwargs)
        self.url="#"
        self.task = task
        self.task_kwargs = task_kwargs

    def process(self, item: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Process button data."""

        url_submit_task = self.request.url_for("submit_task")
        url_detail_task = self.request.url_for("task_details", task_id="__TASK_ID_REPLACE__")

        for key, value in self.task_kwargs.items():
            self.task_kwargs[key] = self.replace_placeholders(self.task_kwargs[key], item=item)

        full_payload = {
            "function": self.task,
            "kwargs": self.task_kwargs,
        }
        # Dump to JSON (double-quoted), then escape any single quotes just in case
        payload_str = full_payload

        js = f"""
           (async () => {{
                const body = {payload_str}
               try {{
                   const response = await fetch('{url_submit_task}?method=json', {{
                       method: 'POST',
                       headers: {{ 'Content-Type': 'application/json' }},
                       body: JSON.stringify(body)
                   }});
                   const data = await response.json();

                   if (data.task_id) {{
                       window.location.href = '{url_detail_task}'.replace('__TASK_ID_REPLACE__', data.task_id);
                   }} else {{
                       alert('Could not start task.');
                   }}
               }} catch (err) {{
                   console.error(err);
                   alert('Network error. Please try again.');
               }}
           }})();
           """

        self.onclick = js
        self.label=f"Run Task {self.task}"

