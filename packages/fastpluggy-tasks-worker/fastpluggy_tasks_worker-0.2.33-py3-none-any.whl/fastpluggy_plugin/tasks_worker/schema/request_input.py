from typing import Optional

from pydantic import BaseModel


class CreateTaskRequest(BaseModel):
    name: Optional[str] = None
    function: str
    #cron: Optional[str] = None
    #interval: Optional[int] = None
    kwargs: dict = {}
    notify_on: list = []

    allow_concurrent: Optional[bool] = True
    max_retries: Optional[int] = 0
    retry_delay: Optional[int] = 3

class CreateScheduledTaskRequest(CreateTaskRequest):
    cron: Optional[str] = None
    interval: Optional[int] = None