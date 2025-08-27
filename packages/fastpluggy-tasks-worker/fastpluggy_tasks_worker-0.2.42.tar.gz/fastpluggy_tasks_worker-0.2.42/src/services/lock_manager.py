import logging
from datetime import datetime
from typing import Dict, List, Tuple


class TaskLock:
    """In-memory representation of a task lock"""
    def __init__(self, task_name: str, task_id: str, acquired_at: datetime, locked_by: str):
        self.task_name = task_name
        self.task_id = task_id
        self.acquired_at = acquired_at
        self.locked_by = locked_by


class TaskLockManager:
    # Class-level storage for locks
    _locks: Dict[str, TaskLock] = {}

    def __init__(self, worker_id: str):
        self.worker_id = worker_id

    def acquire_lock(self, task_name: str, task_id: str) -> bool:
        """
        Try to acquire a lock for the given task.
        Returns True if lock was acquired, False otherwise.
        """
        try:
            # Check if task is already locked
            if task_id in TaskLockManager._locks:
                return False  # Already locked

            # Create a new lock
            lock = TaskLock(
                task_name=task_name,
                task_id=task_id,
                acquired_at=datetime.utcnow(),
                locked_by=self.worker_id
            )

            # Store the lock in memory
            TaskLockManager._locks[task_id] = lock
            return True
        except Exception as e:
            logging.exception(f"Failed to acquire lock for task {task_id}: {e}")
            return False

    def release_lock(self, task_id: str) -> bool:
        """
        Release the lock for the given task if this worker owns it.
        """
        try:
            # Check if lock exists and is owned by this worker
            if task_id in TaskLockManager._locks and TaskLockManager._locks[task_id].locked_by == self.worker_id:
                # Remove the lock
                del TaskLockManager._locks[task_id]
                return True
            return False
        except Exception as e:
            logging.exception(f"Failed to release lock for task {task_id}: {e}")
            return False

    @staticmethod
    def is_locked(task_id: str, db=None) -> bool:
        """
        Check if a lock exists for the given task.
        The db parameter is kept for backward compatibility but is not used.
        """
        return task_id in TaskLockManager._locks

    @staticmethod
    def force_release(task_id: str) -> bool:
        """
        Force release of a lock regardless of who owns it.
        """
        try:
            if task_id in TaskLockManager._locks:
                del TaskLockManager._locks[task_id]
                return True
            return False
        except Exception as e:
            logging.exception(f"Failed to force release lock for task {task_id}: {e}")
            return False

    @staticmethod
    def get_all_locks() -> List[Tuple[str, str, datetime, str]]:
        """
        Return a list of all locks as tuples (task_id, task_name, acquired_at, locked_by).
        This is useful for the admin interface.
        """
        return [(lock.task_id, lock.task_name, lock.acquired_at, lock.locked_by) 
                for lock in TaskLockManager._locks.values()]
