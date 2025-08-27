import logging
from contextlib import contextmanager
from logging import LogRecord
import threading
from typing import Generator, List

from .notifiers.registry import dispatch_log_line
from .schema.context import TaskContext

# Shared thread-local variable
thread_local_context = threading.local()


class ThreadLocalHandler(logging.Handler):
    """
    A logging handler that writes logs to a thread-local list of messages.
    Automatically dispatches logs to the notification system.
    """

    def __init__(self):
        super().__init__()
        self.local = threading.local()

    def emit(self, record: LogRecord) -> None:
        try:
            # Dispatch to WebSocket or other live log consumers
            if hasattr(thread_local_context, "task_id"):
                dispatch_log_line(
                    task_id=getattr(record, "task_id", "unknown"),
                    record=record
                )

            msg = self.format(record)

            #print(f"Log from thread {threading.get_ident()} with task_id={getattr(record, 'task_id', None)} : {msg}")

            # Write to internal list if set
            if hasattr(self.local, "stream"):
                self.local.stream.append(msg)
        except Exception as e:
            print(f"Exception in ThreadLocalHandler.emit: {e}")
            self.handleError(record)

    def set_stream(self, stream: List[str]) -> None:
        """
        Install a list on which we'll append each formatted log line.
        """
        self.local.stream = stream

    def clear_stream(self) -> None:
        if hasattr(self.local, "stream"):
            del self.local.stream

    def get_stream_value(self, join: bool = True) -> List[str] or str:
        """
        If join=True, returns a single string with newlines.
        Otherwise returns the raw list of lines.
        """
        if not hasattr(self.local, "stream"):
            return "" if join else []
        return "\n".join(self.local.stream) if join else list(self.local.stream)


class LoguruToLoggingHandler:
    """
    Bridge for redirecting loguru logs to the standard logging system.
    """

    def __init__(self, level: int = logging.DEBUG):
        self.level = level

    def write(self, message: str) -> None:
        if message.strip():
            logging.getLogger("loguru").log(self.level, message.strip())

    def flush(self) -> None:
        pass


@contextmanager
def log_handler_context(context: TaskContext) -> Generator[ThreadLocalHandler, None, None]:
    """
    Context manager that installs a logging handler which captures logs
    into a thread-local list and dispatches them with a task_id tag.
    """
    logger = logging.getLogger()
    log_lines: List[str] = []

    class TaggedHandler(ThreadLocalHandler):
        def emit(self, record: LogRecord) -> None:
            #print(f" thread_local_context : {thread_local_context.__dict__}")
            record.task_id = getattr(thread_local_context, "task_id", None)
            record.context = getattr(thread_local_context, "context", None)
            super().emit(record)

    handler = TaggedHandler()
    handler.set_stream(log_lines)

    # Bridge loguru → standard logging (track the sink ID so we can remove just it)
    from loguru import logger as loguru_logger
    loguru_logger.remove()
    loguru_sink_id = loguru_logger.add(LoguruToLoggingHandler(), level="DEBUG")

    # Only add if it’s not in logger.handlers already
    if handler not in logger.handlers:
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG)
    thread_local_context.task_id = context.task_id
    thread_local_context.context = context

    try:
        yield handler
    finally:
        if handler in logger.handlers:
            logger.removeHandler(handler)
        handler.clear_stream()
        # Remove only the Loguru sink we added
        loguru_logger.remove()

        delattr(thread_local_context, "task_id")
        delattr(thread_local_context, "context")
