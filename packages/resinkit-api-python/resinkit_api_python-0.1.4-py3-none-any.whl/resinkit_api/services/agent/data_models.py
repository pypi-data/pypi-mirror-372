from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class LogEntry(BaseModel):
    timestamp: str | int | float
    level: str
    message: str


class FlinkJobStatus(Enum):
    """Enum for Flink job statuses."""

    INITIALIZING = "INITIALIZING"
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    FAILING = "FAILING"
    FAILED = "FAILED"
    CANCELLING = "CANCELLING"
    CANCELED = "CANCELED"
    FINISHED = "FINISHED"
    RESTARTING = "RESTARTING"
    SUSPENDED = "SUSPENDED"
    RECONCILING = "RECONCILING"

    # Additional statuses from execution result
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

    def is_terminal(self) -> bool:
        """Check if the status is terminal."""
        return self in [FlinkJobStatus.FINISHED, FlinkJobStatus.FAILED, FlinkJobStatus.CANCELED]


def map_flink_status_to_task_status(flink_status: FlinkJobStatus, job_details: Dict[str, Any] = None):
    """
    Map Flink job status to TaskStatus.

    Args:
        flink_status: The Flink job status
        job_details: Additional job details for more context (used for COMPLETED status)

    Returns:
        Corresponding TaskStatus
    """
    # Import here to avoid circular imports
    from resinkit_api.db.models import TaskStatus

    # Running states
    if flink_status in [
        FlinkJobStatus.RUNNING,
        FlinkJobStatus.CREATED,
        FlinkJobStatus.INITIALIZING,
        FlinkJobStatus.RESTARTING,
        FlinkJobStatus.RECONCILING,
        FlinkJobStatus.FAILING,
        FlinkJobStatus.CANCELLING,
        FlinkJobStatus.IN_PROGRESS,
    ]:
        return TaskStatus.RUNNING
    # Completed states
    elif flink_status in [FlinkJobStatus.FINISHED, FlinkJobStatus.COMPLETED]:
        return TaskStatus.COMPLETED
    elif flink_status == FlinkJobStatus.CANCELED:
        return TaskStatus.CANCELLED
    # Failed states
    elif flink_status in [FlinkJobStatus.FAILED, FlinkJobStatus.SUSPENDED]:
        return TaskStatus.FAILED
    else:
        # Unknown status, return as running by default
        return TaskStatus.RUNNING


# Custom exceptions for API error handling
class TaskError(Exception):
    pass


class InvalidTaskError(TaskError):
    pass


class TaskNotFoundError(TaskError):
    pass


class UnprocessableTaskError(TaskError):
    pass


class TaskConflictError(Exception):
    pass


class TaskExecutionError(TaskError):
    pass


# Pydantic model for task results
class TaskResult(BaseModel):
    task_id: str
    data: Dict[str, Any]
    error_info: Optional[Dict[str, Any]] = None
