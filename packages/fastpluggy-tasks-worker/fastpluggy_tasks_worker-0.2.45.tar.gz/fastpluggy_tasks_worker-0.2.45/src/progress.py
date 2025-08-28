# progress.py
import time
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable


# Hooks you plug into your system:
ProgressSink = Callable[[str, float, Optional[str], Dict[str, Any]], None]

@dataclass
class ProgressState:
    value: float = 0.0                 # 0..100
    message: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)
    ts: float = 0.0

class Progress:
    """
    A process-wide helper that:
      - reads current task from ContextVar
      - debounces updates to avoid DB/WS spam
      - sends to sinks (DB, WebSocket, metrics)
    """
    def __init__(self, *, min_interval: float = 0.2):
        self._min_interval = min_interval
        self._lock = threading.Lock()
        self._last: Dict[str, ProgressState] = {}
        self._sinks: list[ProgressSink] = []

    def register_sink(self, sink: ProgressSink):
        self._sinks.append(sink)

    def _emit(self, task_id: str, value: float, message: Optional[str], meta: Dict[str, Any]):
        # fan-out to registered sinks
        for s in self._sinks:
            try:
                s(task_id, value, message, meta)
            except Exception:
                # never crash callers
                pass

    def update(self, value: float, message: Optional[str] = None, meta: Optional[Dict[str, Any]] = None, *, force: bool = False):
        """
        Update current task's progress.
        value: 0..100
        """
        from . import current_task_ctx
        ctx = current_task_ctx.get()
        if not ctx:
            # outside of a task: ignore or raise (your call)
            return

        task_id = ctx.task_id
        now = time.time()
        meta = meta or {}
        print(f"ctx.task_id : {ctx.task_id}")
        with self._lock:
            prev = self._last.get(task_id)
            if not force and prev and (now - prev.ts) < self._min_interval:
                # debounce
                # still keep the latest for eventual emit
                if value >= (prev.value + 0.01):  # keep a small monotonic guard
                    self._last[task_id] = ProgressState(value, message, meta, prev.ts)
                return

            st = ProgressState(value=value, message=message, meta=meta, ts=now)
            self._last[task_id] = st

        self._emit(task_id, value, message, meta)

    def finish(self, message: Optional[str] = "done", meta: Optional[Dict[str, Any]] = None):
        self.update(100.0, message, meta, force=True)

task_progress = Progress(min_interval=0.25)
