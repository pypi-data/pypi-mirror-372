from celery.schedules import crontab
from loguru import logger

from fastpluggy.core.database import session_scope
from ..repository.scheduled import ensure_scheduled_task_exists


class DummySender:
    def __init__(self):
        self.entries = {}

    def crontab_to_cronexpr(self, cb: crontab) -> str:
        """
        Given a celery.schedules.crontab, return a standard
        'minute hour day-of-month month day-of-week' cron expression.
        """
        dow = cb._orig_day_of_week

        # Only try to convert if dow is a string that contains alphabetic chars
        if isinstance(dow, str) and any(c.isalpha() for c in dow):
            dow_lc = dow.lower()
            name_to_num = {
                "sunday": 0, "sun": 0,
                "monday": 1, "mon": 1,
                "tuesday": 2, "tue": 2,
                "wednesday": 3, "wed": 3,
                "thursday": 4, "thu": 4,
                "friday": 5, "fri": 5,
                "saturday": 6, "sat": 6,
            }

            # 1) Single‐name case, e.g. "sunday" or "mon"
            if dow_lc in name_to_num:
                dow = str(name_to_num[dow_lc])

            # 2) Comma‐separated list, e.g. "mon,wed,fri"
            elif "," in dow_lc:
                parts = [p.strip() for p in dow_lc.split(",")]
                converted = []
                for p in parts:
                    if p in name_to_num:
                        converted.append(str(name_to_num[p]))
                    else:
                        raise ValueError(f"Unrecognized day-of-week name: {p!r}")
                dow = ",".join(converted)

            # 3) Range of names, e.g. "mon-fri"
            elif "-" in dow_lc:
                start, end = [p.strip() for p in dow_lc.split("-", 1)]
                if start in name_to_num and end in name_to_num:
                    dow = f"{name_to_num[start]}-{name_to_num[end]}"
                else:
                    bad = start if start not in name_to_num else end
                    raise ValueError(f"Unrecognized day-of-week name: {bad!r}")

            # 4) Step values (every N days), e.g. "*/2" or "*/3"
            elif dow_lc.startswith("*/"):
                # This covers strings like "*/2", "*/3"
                step = dow_lc[2:]
                if step.isdigit():
                    dow = f"*/{step}"
                else:
                    raise ValueError(f"Invalid day-of-week step: {dow!r}")

            else:
                # If it’s some other format that’s not recognized (e.g. "*/X" where X is not digit),
                # raise an error so you notice it.
                raise ValueError(f"Unrecognized day-of-week name: {dow!r}")

        # If dow was "*", "0,6", "2-5", "3", etc., we leave it unchanged.

        return " ".join([
            str(cb._orig_minute),
            str(cb._orig_hour),
            str(cb._orig_day_of_month),
            str(cb._orig_month_of_year),
            str(dow),
        ])

    def add_periodic_task(self, schedule, signature, name=None, **opts):
        # build a stable key for this entry
        key = name or signature.name

        # normalize schedule into either `cron` or `interval`
        cron_expr = None
        interval  = None

        if isinstance(schedule, crontab):
            cron_expr = self.crontab_to_cronexpr(schedule)
            schedule_repr = cron_expr
        else:
            # Celery allows a numeric interval or objects with .run_every
            if hasattr(schedule, "run_every"):
                interval = schedule.run_every
            elif isinstance(schedule, (int, float)):
                interval = schedule
            else:
                # fallback to repr for weird types
                schedule_repr = repr(schedule)

            schedule_repr = f"every {interval}s" if interval is not None else schedule_repr

        # 1) store in-memory for later inspection
        self.entries[key] = {
            "schedule": schedule_repr,
            "task_name": signature.name,
            "args":      getattr(signature, "args", ()),
            "kwargs":    getattr(signature, "kwargs", {}),
            **opts,
        }

        # 2) persist/upsert via your helper
        try:
            from fastpluggy_plugin.tasks_worker.config import TasksRunnerSettings
            settings = TasksRunnerSettings()
            with session_scope() as db:
                ensure_scheduled_task_exists(
                    db           = db,
                    function     = signature.name,       # or pass the real fn if you have it
                    task_name    = key,
                    cron         = cron_expr,
                    interval     = interval,
                    kwargs       = self.entries[key]["kwargs"],
                    notify_config= None,
                    max_retries  = opts.get("max_retries", 0),
                    retry_delay  = opts.get("retry_delay", 0),
                    enabled = settings.discover_celery_schedule_enabled_status,
                )
                logger.debug(f"[SCHEDULER] Ensured DB entry for '{key}'")
        except Exception as e:
            logger.error(f"[SCHEDULER] Failed to persist '{key}': {e}")
        finally:
            pass

