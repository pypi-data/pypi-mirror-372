import datetime
from datetime import timezone, timedelta

from croniter import croniter
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text

from fastpluggy.core.database import Base


class ScheduledTaskDB(Base):
    __tablename__ = "fp_task_schedule"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    function = Column(String(200), nullable=False)
    cron = Column(String(200), nullable=True)  # e.g. "*/5 * * * *"
    interval = Column(Integer, nullable=True, doc="Interval in seconds")
    enabled = Column(Boolean, default=True, nullable=False)

    kwargs = Column(Text, default="{}")  # JSON‐encoded kwargs
    notify_on = Column(Text, default=None)  # JSON string like {"task_failed": [...]}

    last_attempt = Column(DateTime, nullable=True)
    last_task_id = Column(String(200), nullable=True)
    last_status = Column(String(200), nullable=True)

    def _compute_next_run_from(self, base_dt: datetime.datetime) -> datetime.datetime | None:
        """
        Given a “base” datetime, compute the next run according to either:
          - self.cron  (via croniter)
          - self.interval (base_dt + interval seconds)
        If neither is set or an error occurs, return None.
        Always returns a UTC‐aware datetime if not None.
        """
        # 1) Normalize base_dt to a UTC‐aware datetime
        if base_dt is None:
            base_dt = datetime.datetime.now(timezone.utc)
        elif base_dt.tzinfo is None:
            # treat naive as UTC
            base_dt = base_dt.replace(tzinfo=timezone.utc)
        else:
            # convert any non‐UTC timezone to UTC
            base_dt = base_dt.astimezone(timezone.utc)

        # 2) Cron‐based scheduling
        if self.cron:
            try:
                candidate = croniter(self.cron, base_dt).get_next(datetime.datetime)
            except Exception:
                return None

            # croniter often returns a naive datetime—assume UTC
            if candidate.tzinfo is None:
                return candidate.replace(tzinfo=timezone.utc)
            return candidate.astimezone(timezone.utc)

        # 3) Interval‐based scheduling
        if self.interval:
            try:
                return base_dt + timedelta(seconds=float(self.interval))
            except Exception:
                return None

        # 4) No schedule at all
        return None

    @property
    def next_run(self) -> datetime.datetime | None:
        """
        Compute “next run” from right now.
        In other words: “If I were to ask the scheduler this instant,
        when is the next valid timestamp?”
        """
        return self._compute_next_run_from(datetime.datetime.now(timezone.utc))

    @property
    def expected_next_run(self) -> datetime.datetime | None:
        """
        Compute “expected next run” from the last attempt.
        In other words: “Given the moment we last tried to run,
        what was the next scheduled timestamp?”
        If last_attempt is None, fall back to using now.
        """
        base = self.last_attempt or datetime.datetime.now(timezone.utc)
        return self._compute_next_run_from(base)

    @property
    def is_late(self) -> bool:
        """
        True if our “expected next run” is already in the past (relative to now).
        If expected_next_run is None, we cannot be late.
        """
        expected = self.expected_next_run
        if expected is None:
            return False

        # At this point, expected is already a UTC‐aware datetime
        return datetime.datetime.now(timezone.utc) >= expected
