import concurrent.futures
import logging
import time
import os
import sys
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

T = TypeVar('T')


class InstrumentedThreadPoolExecutor(concurrent.futures.ThreadPoolExecutor):
    """
    A ThreadPoolExecutor that keeps track of running futures and provides methods
    to get information about the executor's state.

    This executor adds task tracking, status reporting, and graceful shutdown capabilities
    to the standard ThreadPoolExecutor.
    """

    def __init__(self, max_workers: Optional[int] = None, thread_name_prefix: str = 'fp'):
        """
        Initialize the executor with tracking dictionaries for futures and tasks.

        Args:
            max_workers: Maximum number of worker threads
            thread_name_prefix: Prefix for worker thread names
        """
        super().__init__(max_workers=max_workers, thread_name_prefix=thread_name_prefix)
        self._running_futures: Dict[concurrent.futures.Future, str] = {}
        self._task_futures: Dict[str, concurrent.futures.Future] = {}
        self._lock = threading.RLock()

    def graceful_shutdown(self, signum=None, frame=None, max_wait=30):
        logging.warning("This is deprecated it should not be call anymore")
        self._graceful_shutdown(signum=signum,frame=frame,max_wait=max_wait)

    def _graceful_shutdown(self, signum=None, frame=None, max_wait=30):
        """
        Signal handler: stop accepting new tasks, cancel pending ones,
        wait for running tasks, then exit.
        Can also be called directly without arguments.

        Args:
            signum: Signal number that triggered the shutdown (if called as signal handler)
            frame: Current stack frame (if called as signal handler)
            max_wait: Maximum time in seconds to wait for tasks to complete
        """

        # Log shutdown initiation
        if signum is not None:
            print(f"⚠️  Caught signal {signum}, shutting down executor…", file=sys.stderr)
        else:
            print("⚠️  Graceful shutdown initiated manually.", file=sys.stderr)

        # Cancel all running futures
        with self._lock:
            for fut in list(self._running_futures):
                logging.info(f"Cancelling running task: {fut}")
                result_cancel = fut.cancel()
                logging.info(f"Result cancelling running task: {fut} : {result_cancel}")

        # Shutdown the executor
        self.shutdown(wait=False, cancel_futures=True)


    def _wait_for_tasks_completion(self, max_wait: int):
        """
        Wait for all running tasks to complete, up to max_wait seconds.

        Args:
            max_wait: Maximum time in seconds to wait for tasks to complete
        """
        start = time.time()
        while True:
            with self._lock:
                unfinished = [f for f in self._running_futures if not f.done()]

            if not unfinished:
                logging.info("All tasks cancelled, shutting down executor.")
                break

            elapsed = time.time() - start
            if elapsed > max_wait:
                logging.error(f"⏳ Shutdown timeout ({max_wait}s) exceeded; force‐killing process")
                # os._exit bypasses cleanup and tears down all threads immediately
                os._exit(1)

            for f in unfinished:
                logging.info(f"⏳  Waiting for task {f!r} (state={f._state})")
            # sleep a bit before re-checking
            time.sleep(0.5)

        print("✅ Executor shut down. Exiting.")

    def submit(self, fn: Callable[..., T], *args: Any, **kwargs: Any) -> concurrent.futures.Future[T]:
        """
        Submit a callable to be executed with the given arguments.

        Args:
            fn: The callable to execute
            *args: Positional arguments for the callable
            **kwargs: Keyword arguments for the callable

        Returns:
            A Future representing the execution of the callable
        """
        # Submit the task to the parent class
        future = super().submit(fn, *args, **kwargs)

        # Track the future
        self._track_future(future)

        return future

    def _track_future(self, future: concurrent.futures.Future) -> None:
        """
        Track a future in the running futures dictionary and set up its done callback.

        Args:
            future: The future to track
        """
        with self._lock:
            self._running_futures[future] = threading.current_thread().name

        def _done_callback(future: concurrent.futures.Future) -> None:
            with self._lock:
                # Remove from running futures
                self._running_futures.pop(future, None)

                # Remove from task_futures if present
                task_ids_to_remove = [task_id for task_id, f in self._task_futures.items() if f == future]
                for task_id in task_ids_to_remove:
                    self._task_futures.pop(task_id, None)

        future.add_done_callback(_done_callback)

    def submit_task(self, task_id: str, fn: Callable[..., T], *args: Any, **kwargs: Any) -> concurrent.futures.Future[T]:
        """
        Submit a callable to be executed with the given arguments and associate it with a task ID.

        Args:
            task_id: A unique identifier for the task
            fn: The callable to execute
            *args: Positional arguments for the callable
            **kwargs: Keyword arguments for the callable

        Returns:
            A Future representing the execution of the callable
        """
        # Submit the task using the standard submit method
        future = self.submit(fn, *args, **kwargs)

        # Associate the future with the task ID
        with self._lock:
            self._task_futures[task_id] = future

        return future

    def get_active_count(self) -> int:
        """
        Get the number of active threads in the executor.

        Returns:
            The number of active threads
        """
        with self._lock:
            return len(self._running_futures)

    def get_running_futures(self) -> List[concurrent.futures.Future]:
        """
        Get a list of all running futures.

        Returns:
            A list of running futures
        """
        with self._lock:
            return list(self._running_futures.keys())

    def get_task_status(self, task_id: str) -> str:
        """
        Return the status of a task based on its Future state.

        Returns:
            One of: "not_found", "running", "done", "cancelled", "pending"
        """
        with self._lock:
            future = self._task_futures.get(task_id)

        if not future:
            return "not_found"
        if future.running():
            return "running"
        elif future.done():
            return "done"
        elif future.cancelled():
            return "cancelled"
        return "pending"

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task using its future, if it exists and is not already done.

        Returns:
            True if the cancellation call was successful.
        """
        with self._lock:
            future = self._task_futures.get(task_id)

        return future.cancel() if future and not future.done() else False

    def get_all_active_tasks(self) -> List[Tuple[str, str]]:
        """
        Return a list of tuples (task_id, status) for all tasks.

        Returns:
            A list of (task_id, status) tuples
        """
        with self._lock:
            task_ids = list(self._task_futures.keys())

        return [(task_id, self.get_task_status(task_id)) for task_id in task_ids]

    def is_running(self):
        return not self._shutdown
