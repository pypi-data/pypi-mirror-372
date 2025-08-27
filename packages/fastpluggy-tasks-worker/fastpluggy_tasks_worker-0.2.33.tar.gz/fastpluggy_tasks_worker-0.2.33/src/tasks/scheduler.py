# tasks/scheduler.py

import asyncio
import json
import logging
import datetime
from datetime import timezone
from typing import Annotated

from sqlalchemy import select
from fastpluggy.core.database import session_scope
from fastpluggy.core.tools.inspect_tools import InjectDependency
from fastpluggy.fastpluggy import FastPluggy
from loguru import logger

from ..models.scheduled import ScheduledTaskDB
from ..task_registry import task_registry


@task_registry.register(name="schedule_loop", allow_concurrent=False)
async def schedule_loop(fast_pluggy: Annotated[FastPluggy, InjectDependency]):
    """
    Main scheduling coroutine.  On each tick, it:
      1. Loads all enabled ScheduledTaskDB records.
      2. For each task, computes expected_next_run (based on last_attempt).
      3. If expected_next_run is not None AND now ≥ expected_next_run, dispatch the task:
         a. Update last_attempt = now.
         b. Submit the task to the worker.
         c. Record last_task_id.
      4. Sleep for scheduler_frequency seconds and repeat.
    """
    from ..config import TasksRunnerSettings

    settings = TasksRunnerSettings()
    logging.info("[SCHEDULER] Starting schedule loop")

    while settings.scheduler_enabled:
        logging.debug("[SCHEDULER] Schedule loop running")

        # If the tasks‐worker executor has been stopped, break out
        worker = fast_pluggy.get_global("tasks_worker").executor
        if not worker.is_running():
            logging.debug("[SCHEDULER] Executor not running → exiting scheduler")
            break

        now_utc = datetime.datetime.now(timezone.utc)
        try:
            with session_scope() as db:
                # 1) Fetch all enabled tasks from the database
                stmt = select(ScheduledTaskDB).where(ScheduledTaskDB.enabled == True)
                all_tasks = db.execute(stmt).scalars().all()

                if not all_tasks:
                    logger.debug("[SCHEDULER] No enabled tasks in DB.")
                else:
                    # 2) Iterate over each scheduled task
                    for sched in all_tasks:
                        try:
                            should_run = sched.is_late
                            print(f"[SCHEDULER] Expected next run for {sched.name} is {should_run}: (now : {now_utc}")

                            # 3) If now ≥ expected_next_run, we should fire this task
                            if should_run:
                                # a) Mark last_attempt = now_utc and persist
                                sched.last_attempt = now_utc
                                db.add(sched)
                                db.commit()

                                # b) Lookup the function by name
                                func = task_registry.get(sched.function)
                                if not func:
                                    logger.warning(
                                        f"[SCHEDULER] Function not found: {sched.function}"
                                    )
                                    continue

                                logger.info(f"[SCHEDULER] Triggering task: {sched.name}")

                                # c) Parse kwargs JSON
                                try:
                                    kw = json.loads(sched.kwargs or "{}")
                                except Exception as parse_err:
                                    logger.exception(
                                        f"[SCHEDULER] Invalid kwargs for {sched.name}: {parse_err}"
                                    )
                                    continue

                                # d) Submit the task to the worker
                                task_id = fast_pluggy.get_global("tasks_worker").submit(
                                    func,
                                    task_name=sched.name,
                                    notify_config=json.loads(sched.notify_on or "[]"),
                                    task_origin="scheduler",
                                    kwargs=kw,
                                    extra_context={"schedule_id": sched.id}
                                )

                                # e) Record last_task_id and commit
                                sched.last_task_id = task_id
                                db.add(sched)
                                db.commit()

                        except Exception as task_error:
                            logger.exception(
                                f"[SCHEDULER] Error scheduling task '{sched.name}': {task_error}"
                            )
                            db.rollback()

        except Exception as e:
            logger.exception(f"[SCHEDULER] Error in main scheduling loop: {e}")

        # 4) Sleep until next tick
        await asyncio.sleep(settings.scheduler_frequency)
