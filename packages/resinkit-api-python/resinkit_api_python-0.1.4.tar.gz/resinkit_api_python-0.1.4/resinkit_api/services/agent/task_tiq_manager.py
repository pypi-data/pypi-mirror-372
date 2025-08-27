"""
TaskIQ-based Task Manager

An alternative task manager implementation using TaskIQ library for distributed task execution.
"""

import asyncio
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session
from taskiq import AsyncTaskiqTask

from resinkit_api.core.logging import get_logger
from resinkit_api.db import tasks_crud
from resinkit_api.db.database import get_db
from resinkit_api.db.models import Task, TaskStatus
from resinkit_api.db.variables_crud import get_all_variables_decrypted
from resinkit_api.services.agent.data_models import (
    LogEntry,
    TaskConflictError,
    TaskNotFoundError,
    TaskResult,
    UnprocessableTaskError,
)
from resinkit_api.services.agent.runner_registry import get_runner_for_task_type
from resinkit_api.services.agent.task_base import TaskBase
from resinkit_api.services.agent.taskiq_broker import get_taskiq_broker, get_taskiq_result_backend

logger = get_logger(__name__)


class TaskTiqManager:
    """
    TaskIQ-based task manager that handles task execution using TaskIQ distributed task queue.
    """

    def __init__(self):
        self.broker = get_taskiq_broker()
        self.result_backend = get_taskiq_result_backend()
        self._active_tasks: Dict[str, TaskBase] = {}  # Track active TaskIQ results
        self._cleanup_interval = 60  # Check for expired tasks every 60 seconds
        self._cleanup_task: Optional[asyncio.Task] = None
        logger.info("TaskTiqManager initialized with broker: %s", type(self.broker).__name__)

    async def submit_task(self, payload: dict, db: Session) -> dict:
        """Submit a task for execution using TaskIQ."""
        TaskBase.validate(payload)

        # TODO: extract DAO from payload and avoid extracting fields here
        task_type = payload.get("task_type")
        name = payload.get("name")
        description = payload.get("description")

        # Extract optional fields
        priority = payload.get("priority", 0)
        created_by = payload.get("created_by", "system")
        notification_config = payload.get("notification_config")
        tags = payload.get("tags")

        # Generate a unique task ID using TaskBase
        task_id = TaskBase.generate_task_id(task_type)
        payload["task_id"] = task_id
        logger.info("Generated task_id: %s for task type: %s", task_id, task_type)

        try:
            # Create task in the database
            logger.debug("Creating task in database: task_id=%s", task_id)
            db_task = tasks_crud.create_task(
                db=db,
                task_id=task_id,
                task_type=task_type,
                task_name=name,
                description=description,
                priority=priority,
                submitted_configs=payload,
                created_by=created_by,
                notification_config=notification_config,
                tags=tags,
            )
            logger.info("Task created in database: task_id=%s, status=%s", task_id, db_task.status.value)
            taskiq_task: AsyncTaskiqTask = await self._execute_task_via_taskiq.kiq(task_id=task_id)
            self._active_tasks[task_id] = taskiq_task
            logger.info("Task submitted to TaskIQ: task_id=%s", task_id)

            # Return the task information
            return {
                "task_id": db_task.task_id,
                "task_type": db_task.task_type,
                "name": db_task.task_name,
                "description": db_task.description,
                "status": db_task.status.value,
                "message": f"Task '{name}' submitted successfully",
                "created_at": db_task.created_at.isoformat(),
                "_links": {"self": {"href": f"/api/v1/agent/tasks/{task_id}"}},
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create task: {str(e)}", exc_info=True)
            raise UnprocessableTaskError(f"Failed to create task: {str(e)}")

    async def get_task_details(self, task_id: str, db: Session) -> dict:
        """Get task details including status updates from TaskIQ if available."""
        logger.info("Getting details for task_id=%s", task_id)

        # Find the task in the database
        db_task: Task = tasks_crud.get_task(db=db, task_id=task_id)

        if not db_task:
            logger.warning("Task not found: task_id=%s", task_id)
            raise TaskNotFoundError(f"Task with ID {task_id} not found")

        db_task = await self._update_task_from_taskiq_result(db, db_task, self._active_tasks.get(task_id))

        # Convert the database model to a dictionary response
        return {
            "task_id": db_task.task_id,
            "task_type": db_task.task_type,
            "name": db_task.task_name,
            "description": db_task.description,
            "status": db_task.status.value,
            "priority": db_task.priority,
            "created_at": db_task.created_at.isoformat(),
            "updated_at": db_task.updated_at.isoformat(),
            "started_at": db_task.started_at.isoformat() if db_task.started_at else None,
            "finished_at": db_task.finished_at.isoformat() if db_task.finished_at else None,
            "expires_at": db_task.expires_at.isoformat() if db_task.expires_at else None,
            "submitted_configs": db_task.submitted_configs,
            "error_info": db_task.error_info,
            "result_summary": db_task.result_summary,
            "execution_details": db_task.execution_details,
            "progress_details": db_task.progress_details,
            "created_by": db_task.created_by,
            "notification_config": db_task.notification_config,
            "tags": db_task.tags,
            "_links": {"self": {"href": f"/api/v1/agent/tasks/{task_id}"}},
        }

    async def list_tasks(
        self,
        db: Session,
        task_type: Optional[str],
        status_: Optional[str],
        task_name_contains: Optional[str],
        tags_include_any: Optional[str],
        created_after: Optional[str],
        created_before: Optional[str],
        limit: Optional[int],
        page_token: Optional[str],
        sort_by: Optional[str],
        sort_order: Optional[str],
    ) -> dict:
        """List tasks with filtering support."""
        logger.info("Listing tasks with filters: type=%s, status=%s, limit=%s", task_type, status_, limit)
        status = TaskStatus[status_] if status_ else None
        limit = limit or 100
        skip = 0

        if page_token:
            try:
                import base64
                import json

                # Decode the page token to get the skip value
                decoded_token = base64.b64decode(page_token).decode("utf-8")
                token_data = json.loads(decoded_token)
                skip = token_data.get("offset", 0)
                logger.debug("Using page_token, skip set to: %d", skip)
            except Exception as e:
                logger.warning("Invalid page_token: %s, error: %s", page_token, str(e))
                skip = 0

        # Convert date strings to datetime objects if provided
        created_after_date = datetime.fromisoformat(created_after) if created_after else None
        created_before_date = datetime.fromisoformat(created_before) if created_before else None

        logger.debug("Querying tasks with filters: status=%s, type=%s, name_contains=%s, tags=%s", status, task_type, task_name_contains, tags_include_any)

        # Process sort parameters
        sort_params = None
        if sort_by:
            direction = 1 if sort_order and sort_order.upper() == "ASC" else -1
            sort_params = {sort_by: direction}
            logger.debug("Sorting by %s, direction: %s", sort_by, "ASC" if direction == 1 else "DESC")

        # Query tasks with filters (request one more than limit to check for more results)
        query_limit = limit + 1
        tasks = tasks_crud.get_tasks(
            db=db,
            skip=skip,
            limit=query_limit,
            status=status,
            task_type=task_type,
            created_after=created_after_date,
            created_before=created_before_date,
            task_name_contains=task_name_contains,
            tags_include_any=tags_include_any.split(",") if tags_include_any else None,
            sort_params=sort_params,
        )

        # Determine if there are more results
        has_more = len(tasks) > limit
        tasks = tasks[:limit]  # Trim to requested limit

        logger.info("Found %d tasks matching filters", len(tasks))

        # Format response
        task_list = []
        for task in tasks:
            task_dict = {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "name": task.task_name,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "finished_at": task.finished_at.isoformat() if task.finished_at else None,
                "expires_at": task.expires_at.isoformat() if task.expires_at else None,
                "created_by": task.created_by,
                "tags": task.tags,
                "_links": {"self": {"href": f"/api/v1/agent/tasks/{task.task_id}"}},
            }
            task_list.append(task_dict)

        # Generate next page token if there are more results
        next_page_token = None
        if has_more:
            import base64

            import orjson

            next_offset = skip + limit
            token_data = {"offset": next_offset}
            next_page_token = base64.b64encode(orjson.dumps(token_data)).decode("utf-8")

        return {
            "tasks": task_list,
            "pagination": {
                "limit": limit,
                "has_more": has_more,
                "next_page_token": next_page_token,
            },
        }

    async def cancel_task(self, task_id: str, db: Session, force: bool = False) -> dict:
        """Cancel a task."""
        logger.info("Cancelling task: task_id=%s, force=%s", task_id, force)

        db_task: Task = tasks_crud.get_task(db=db, task_id=task_id)

        if not db_task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")

        # Check if task is in a cancellable state
        if db_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            if not force:
                raise TaskConflictError(f"Task {task_id} is already in final state: {db_task.status.value}")

        try:
            runner = get_runner_for_task_type(db_task.task_type)
            await runner.cancel(runner.from_dao(db_task), force=force)
            logger.info("Marking TaskIQ task as cancelled: task_id=%s", task_id)
        except Exception as e:
            logger.error("Error cancelling TaskIQ task: %s", str(e))

        # Update task status to CANCELLED
        logger.info("Updating task status to CANCELLED: task_id=%s", task_id)
        updated_task = tasks_crud.update_task_status(
            db=db,
            task_id=task_id,
            new_status=TaskStatus.CANCELLED,
            actor="user" if not force else "system",
        )

        # Remove from active tasks
        if task_id in self._active_tasks:
            self._active_tasks.pop(task_id, None)

        return {
            "task_id": task_id,
            "status": updated_task.status.value,
            "message": f"Task {task_id} has been cancelled",
            "cancelled_at": updated_task.updated_at.isoformat(),
        }

    async def get_task_logs(
        self,
        task_id: str,
        db: Session,
        log_type: Optional[str] = None,
        since_timestamp: Optional[str] = None,
        since_token: Optional[str] = None,
        limit_lines: Optional[int] = None,
        log_level_filter: Optional[str] = "INFO",
    ) -> List[LogEntry]:
        """Get task logs."""
        logger.info("Getting logs for task: task_id=%s", task_id)

        db_task: Task = tasks_crud.get_task(db=db, task_id=task_id)

        if not db_task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")

        try:
            runner = get_runner_for_task_type(db_task.task_type)
            task_base = runner.from_dao(db_task)

            # Get logs from the runner using get_log_summary method
            logs = runner.get_log_summary(task_base, level=log_level_filter)

            logger.debug("Retrieved %d log entries for task: task_id=%s", len(logs), task_id)
            return logs

        except Exception as e:
            logger.error("Error getting task logs: %s", str(e))
            return []

    async def get_task_results(self, task_id: str, db: Session) -> TaskResult:
        """Get task results."""
        logger.info("Getting results for task: task_id=%s", task_id)

        db_task: Task = tasks_crud.get_task(db=db, task_id=task_id)

        if not db_task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")

        # Check TaskIQ result if available
        db_task = await self._update_task_from_taskiq_result(db, db_task, self._active_tasks.get(task_id))

        return TaskResult(
            task_id=task_id,
            data=db_task.result_summary or {},
            error_info=db_task.error_info,
        )

    async def permanently_delete_task(self, task_id: str, db: Session) -> None:
        """Permanently delete a task."""
        logger.info("Permanently deleting task: task_id=%s", task_id)

        db_task: Task = tasks_crud.get_task(db=db, task_id=task_id)
        if not db_task:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")

        runner = get_runner_for_task_type(db_task.task_type)
        dto_task = runner.from_dao(db_task)

        if not dto_task.status.is_terminal():
            # cancel the task
            await runner.cancel(dto_task, force=True)

        # Remove from active tasks if present
        self._active_tasks.pop(task_id, None)

        # Delete task events first
        tasks_crud.delete_task_events(db=db, task_id=task_id)

        # Delete the task (this does soft delete by setting active=False)
        tasks_crud.delete_task(db=db, task_id=task_id)

        logger.info("Task permanently deleted: task_id=%s", task_id)

    # TaskIQ task execution function
    @property
    def _execute_task_via_taskiq(self):
        """Get the TaskIQ task function."""
        if not hasattr(self, "_taskiq_func"):

            @self.broker.task
            async def execute_task_taskiq(task_id: str) -> Dict[str, Any]:
                """TaskIQ task function for executing tasks."""
                logger.info("TaskIQ: Starting execution of task: task_id=%s", task_id)
                # Note: TaskIQ background tasks need their own database session
                db = next(get_db())

                try:
                    # Get the task from the database
                    db_task: Task = tasks_crud.get_task(db=db, task_id=task_id)
                    if not db_task:
                        error_msg = f"Task not found: {task_id}"
                        logger.error(error_msg)
                        raise TaskNotFoundError(error_msg)

                    # Update task status to VALIDATING
                    logger.info("TaskIQ: Updating task status to VALIDATING: task_id=%s", task_id)
                    db_task = tasks_crud.update_task_status(db=db, task_id=task_id, new_status=TaskStatus.VALIDATING, actor="taskiq")

                    # Validate the task configuration
                    logger.info("TaskIQ: Validating task configuration: task_id=%s", task_id)
                    runner = get_runner_for_task_type(db_task.task_type)
                    runner.validate_config(db_task.submitted_configs)
                    logger.debug("TaskIQ: Task configuration validated successfully: task_id=%s", task_id)

                    # Update task status to PREPARING
                    logger.info("TaskIQ: Updating task status to PREPARING: task_id=%s", task_id)
                    db_task = tasks_crud.update_task_status(db=db, task_id=task_id, new_status=TaskStatus.PREPARING, actor="taskiq")

                    # Submit the task to the runner
                    logger.info("TaskIQ: Submitting task to runner: task_id=%s", task_id)
                    # Get all variables from the database for variable substitution
                    logger.debug("TaskIQ: Fetching variables for substitution: task_id=%s", task_id)
                    variables_dict = await get_all_variables_decrypted(db)

                    # Create task with variable substitution
                    task_base = await runner.submit_task(runner.from_dao(db_task, variables=variables_dict))
                    db_task = tasks_crud.update_task_status(
                        db=db,
                        task_id=task_id,
                        new_status=task_base.status,
                        actor="taskiq",
                        execution_details=task_base.execution_details,
                        result_summary=task_base.result_summary,
                        error_info=task_base.error_info,
                    )

                    return {
                        "task_id": task_id,
                        "status": db_task.status.value,
                        "result_summary": db_task.result_summary,
                        "execution_details": db_task.execution_details,
                        "error_info": db_task.error_info,
                    }

                except Exception as e:
                    logger.error(f"TaskIQ: Error executing task {task_id}: {str(e)}", exc_info=True)
                    raise

            self._taskiq_func = execute_task_taskiq

        return self._taskiq_func

    async def _update_task_from_taskiq_result(self, db: Session, db_task: Task, taskiq_task: AsyncTaskiqTask | None = None) -> Task:
        """Update task status based on TaskIQ result."""
        is_taskiq_ready: bool = taskiq_task and await taskiq_task.is_ready()
        if is_taskiq_ready:
            self._active_tasks.pop(db_task.task_id, None)

        if db_task.result_summary and db_task.result_summary.get("all_jobs_finished") is True:
            return db_task

        runner = get_runner_for_task_type(db_task.task_type)
        dto_task = await runner.fetch_task_status(runner.from_dao(db_task))
        db_task = tasks_crud.update_task_status(
            db=db,
            task_id=db_task.task_id,
            new_status=dto_task.status,
            actor="taskiq",
            error_info=dto_task.error_info,
            result_summary=dto_task.result_summary,
            execution_details=dto_task.execution_details,
        )

        if dto_task.status.is_terminal():
            self._active_tasks.pop(db_task.task_id, None)

        return db_task

    async def start_expired_tasks_monitor(self) -> None:
        """Start the background task to monitor and cancel expired tasks."""
        logger.info("Starting expired tasks monitor")
        pass

    async def stop_expired_tasks_monitor(self) -> None:
        """Stop the background task monitor."""
        logger.info("Stopping expired tasks monitor")
        pass

    async def _check_and_cancel_expired_tasks(self) -> None:
        """Check for expired tasks and cancel them."""
        logger.debug("Checking for expired tasks")

        # Note: Background monitoring tasks need their own database session
        db = next(get_db())
        # Use UTC datetime for consistency
        now = datetime.now(UTC)

        try:
            # Find tasks that are expired and still running
            expired_tasks = tasks_crud.get_tasks(
                db=db,
                status=None,  # Check all statuses
                limit=1000,  # Reasonable limit for cleanup
            )

            for task in expired_tasks:
                # Check if task is expired and in a running state
                # Use timestamp comparison to avoid timezone issues
                is_expired = False
                if task.expires_at:
                    is_expired = now.timestamp() > task.expires_at.timestamp()

                if is_expired and not task.status.is_terminal():
                    logger.info("Found expired task, cancelling: task_id=%s, expires_at=%s", task.task_id, task.expires_at)

                    try:
                        await self.cancel_task(task.task_id, db, force=True)
                    except Exception as e:
                        logger.error("Error cancelling expired task %s: %s", task.task_id, str(e))

        except Exception as e:
            logger.error("Error checking for expired tasks: %s", str(e))
