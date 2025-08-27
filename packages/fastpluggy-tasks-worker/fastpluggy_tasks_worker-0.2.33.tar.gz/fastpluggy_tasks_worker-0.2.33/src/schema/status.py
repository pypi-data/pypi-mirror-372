from enum import Enum


class TaskStatus(str, Enum):
    CREATED ="created"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    MANUAL_CANCELLED = "manual_cancelled"
    SKIPPED = "skipped"
    ERROR = "error"
    TIMEOUT = "timeout"

    #PENDING = "Pending"  # Sent to executor
    #COMPLETED = "Completed"

    @property
    def badge_class(self):
        return {
            TaskStatus.CREATED: 'bg-secondary',
            TaskStatus.QUEUED: 'bg-info',
            TaskStatus.RUNNING: 'bg-primary',
            TaskStatus.SUCCESS: 'bg-success',
            TaskStatus.FAILED: 'bg-danger',
            TaskStatus.CANCELLED: 'bg-warning',
            TaskStatus.MANUAL_CANCELLED: 'bg-warning',
            TaskStatus.TIMEOUT: 'bg-warning',
        }.get(self, 'bg-secondary')  # Default to 'bg-secondary' if not found
