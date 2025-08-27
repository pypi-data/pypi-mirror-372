import logging
import uuid


class DummyTask:
    """
    Dummy task to inject into a celery task to replace self
    """
    def update_state(self, **kwargs):
        logging.info(f"DummyTask.update_state({kwargs})")


class DummyAsyncResult:
    """
    A dummy stand-in for celery.result.AsyncResult.
    """
    def __init__(self, task_id=None):
        # generate a UUID if none passed
        self.id = task_id or str(uuid.uuid4())
        # some people refer to .task_id
        self.task_id = self.id

        # default state/result
        self.state = 'UNK'
        #self.result = None
        #self.traceback = None

    def __repr__(self):
        return f"<DummyAsyncResult id={self.id!r} state={self.state!r}>"

    @property
    def status(self):
        # celery.AsyncResult.status is an alias for .state
        return self.state

    def ready(self):
        """True if the task has finished (success or failure)."""
        return self.state not in ('PENDING', 'RECEIVED', 'STARTED')

    def successful(self):
        """True if the task finished without raising an exception."""
        return self.state == 'SUCCESS'

    def failed(self):
        """True if the task raised an exception."""
        return self.state == 'FAILURE'

    def get(self, timeout=None, propagate=True):
        """
        Block until the task finishes and return the result, or
        re-raise the exception if propagate=True.
        """
        if not self.ready():
            raise TimeoutError(f"Task {self.id!r} not ready (state={self.state})")
        if self.failed() and propagate:
            # simulate re-raising the original exception
            raise Exception(f"Task {self.id!r} failed")
        return self.result
