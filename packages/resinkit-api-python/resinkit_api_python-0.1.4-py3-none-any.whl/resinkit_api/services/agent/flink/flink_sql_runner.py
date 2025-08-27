import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
from flink_gateway_api import Client as FlinkGatewayClient
from flink_gateway_api.api.default import (
    execute_statement,
    open_session,
)
from flink_gateway_api.models import (
    ExecuteStatementRequestBody,
    ExecuteStatementResponseBody,
    OpenSessionRequestBody,
    OpenSessionResponseBody,
)

from resinkit_api.clients.job_manager.flink_job_manager_client import FlinkJobManager
from resinkit_api.clients.sql_gateway.flink_utils import (
    FlinkSqlGatewayNotFoundException,
    ResultsFetchOpts,
)
from resinkit_api.core.logging import get_logger
from resinkit_api.db.models import Task, TaskStatus
from resinkit_api.services.agent.common.log_file_manager import LogFileManager
from resinkit_api.services.agent.data_models import FlinkJobStatus, map_flink_status_to_task_status
from resinkit_api.services.agent.flink.flink_resource_manager import FlinkResourceManager, FlinkResourcesResult
from resinkit_api.services.agent.flink.flink_sql_task import FlinkSQLTask
from resinkit_api.services.agent.task_base import TaskBase
from resinkit_api.services.agent.task_runner_base import LogEntry, TaskRunnerBase

logger = get_logger(__name__)

DEFAULT_POLLING_OPTIONS = ResultsFetchOpts(
    max_poll_secs=30,
    poll_interval_secs=0.5,
    n_row_limit=100,
)


def _df_to_json(df: pd.DataFrame) -> Dict[str, Any]:
    return json.loads(df.to_json(orient="records", date_format="iso"))


class FlinkSQLRunner(TaskRunnerBase):
    """Runner for executing Flink SQL jobs via the SQL Gateway."""

    def __init__(self, job_manager: FlinkJobManager, sql_gateway_client: FlinkGatewayClient, runtime_env: dict | None = None):
        """
        Initialize the Flink SQL Runner.

        Args:
            job_manager: FlinkJobManager instance for job management
            sql_gateway_client: FlinkGatewayClient instance for SQL Gateway interaction
            runtime_env: Optional runtime environment configuration
        """
        super().__init__(runtime_env or {})
        self.job_manager = job_manager
        self.sql_gateway_client = sql_gateway_client
        self.resource_manager = FlinkResourceManager()
        self.tasks: Dict[str, FlinkSQLTask] = {}

    @classmethod
    def validate_config(cls, task_config: dict) -> None:
        """
        Validates the configuration for running a Flink SQL job.

        Args:
            task_config: The task configuration dictionary

        Raises:
            ValueError: If the configuration is invalid
        """
        try:
            FlinkSQLTask.validate(task_config)
        except Exception as e:
            raise ValueError(f"Invalid Flink SQL configuration: {str(e)}")

    def from_dao(self, dao: Task, variables: Dict[str, Any] | None = None) -> FlinkSQLTask:
        """
        Create a FlinkSQLRunner instance from a Task DAO.

        Args:
            dao: The Task DAO

        Returns:
            The FlinkSQLRunner instance
        """
        return FlinkSQLTask.from_dao(dao, variables)

    async def submit_task(self, task: FlinkSQLTask) -> FlinkSQLTask:
        """
        Submits a Flink SQL job to the SQL Gateway.

        Args:
            task: The task instance

        Returns:
            The created task instance, with updated:
            - status
            - result_summary
            - execution_details
            - if failed, error_info will be set

        Raises:
            TaskExecutionError: If job submission fails
        """
        task_id = task.task_id
        self.tasks[task_id] = task

        # Process resources
        resources: FlinkResourcesResult = await self.resource_manager.process_resources(task.resources)

        lfm = LogFileManager(task.log_file, limit=1000, logger=logger)

        try:
            # Update task status
            task.status = TaskStatus.RUNNING
            if task.result_summary is None:
                task.result_summary = {}
            if task.result_summary.get("results") is None:
                task.result_summary["results"] = []
            if task.result_summary.get("job_ids") is None:
                task.result_summary["job_ids"] = []
            if task.result_summary.get("is_query") is None:
                task.result_summary["is_query"] = []
            lfm.info(f"Starting Flink SQL job: {task.name}")

            # Create session properties
            session_properties = self._create_session_properties(task, resources)
            session_name = f"session_{task_id}"

            session_response: OpenSessionResponseBody = await open_session.asyncio(
                client=self.sql_gateway_client,
                body=OpenSessionRequestBody.from_dict(
                    {
                        "properties": session_properties,
                        "sessionName": session_name,
                    }
                ),
            )

            if not session_response:
                raise Exception("Failed to open Flink session")

            session_handle = session_response.session_handle
            lfm.info(f"Created Flink SQL session: {session_handle}")

            try:
                # Execute each SQL statement
                operation_handles = []
                for i, sql in enumerate(task.sql_statements):
                    lfm.info(f"Executing SQL statement {i+1}/{len(task.sql_statements)}")
                    lfm.info(f"SQL: {sql}")

                    # Execute the statement
                    execute_response: ExecuteStatementResponseBody = await execute_statement.asyncio(
                        client=self.sql_gateway_client,
                        body=ExecuteStatementRequestBody.from_dict({"statement": sql}),
                    )

                    if not execute_response:
                        raise Exception("Failed to execute statement")

                    operation_handle = execute_response.operation_handle
                    operation_handles.append(operation_handle)

                    # Fetch results with polling
                    result_data = await self._fetch_operation_results(session_handle, operation_handle, task.connection_timeout_seconds, lfm)

                    # Store results
                    if result_data.get("results"):
                        task.result_summary["results"].append(result_data["results"])
                    if result_data.get("job_id"):
                        task.result_summary["job_ids"].append(result_data["job_id"])

                        # Fetch job exceptions if available
                        try:
                            job_exceptions = await self.job_manager.get_job_exceptions(result_data["job_id"])
                            if "job_exceptions" not in task.result_summary:
                                task.result_summary["job_exceptions"] = []
                            task.result_summary["job_exceptions"].append(job_exceptions)
                        except Exception as e:
                            lfm.error(f"Failed to fetch job information for {result_data['job_id']}: {str(e)}")

                    # Check operation status
                    if result_data.get("status") == "FINISHED" and i == len(task.sql_statements) - 1:
                        task.status = TaskStatus.COMPLETED
                        lfm.info(f"Flink SQL job completed successfully, name: {task.name}, id: {task.task_id}")
                    else:
                        lfm.info(f"Flink SQL job submitted successfully, name: {task.name}, id: {task.task_id}, status: {result_data.get('status')}")
            finally:
                # Close session
                try:
                    await self.sql_gateway_client.sessions.close_session.asyncio_detailed(session_handle=session_handle)
                except Exception as e:
                    lfm.error(f"Failed to close session: {str(e)}")

            # Update execution_details with important execution information
            task.execution_details = {
                "log_file": task.log_file,
                "session_name": session_name,
                "session_id": session_handle,
                "operation_ids": operation_handles,
                "job_ids": [jid for jid in task.result_summary.get("job_ids", []) if jid],
            }
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_info = {"error": str(e), "error_type": e.__class__.__name__, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            lfm.error(f"Failed to submit Flink SQL job: {str(e)}")
        return task

    def get_status(self, task: TaskBase) -> TaskStatus:
        """
        Gets the status of a submitted Flink SQL job.

        Args:
            task: The task instance

        Returns:
            The task status
        """
        if not task:
            return TaskStatus.UNKNOWN
        return task.status

    def get_result(self, task: FlinkSQLTask) -> Optional[Any]:
        """
        Gets the result of a completed Flink SQL job.

        Args:
            task: The task instance

        Returns:
            The task result
        """
        if not task:
            return None
        return task.result

    def get_log_summary(self, task: FlinkSQLTask, level: str = "INFO") -> List[LogEntry]:
        """
        Gets a summary of logs for a Flink SQL job.

        Args:
            task: The task instance
            level: The log level to filter by

        Returns:
            A list of log entries
        """
        if not task or not task.log_file or not os.path.exists(task.log_file):
            return []

        try:
            lfm = LogFileManager(task.log_file, limit=1000, logger=logger)
            entries = lfm.get_entries(level=level)
            return entries
        except Exception as e:
            logger.error(f"Failed to read logs for task {task.task_id}: {str(e)}")
            return [LogEntry(timestamp=datetime.now().timestamp(), level="ERROR", message=f"Error reading logs: {str(e)}")]

    async def cancel(self, task: FlinkSQLTask, force: bool = False) -> FlinkSQLTask:
        """
        Cancels a running Flink SQL job.

        Args:
            task: The task instance
            force: Whether to force cancel the job

        Returns:
            The updated task instance

        Raises:
            TaskExecutionError: If cancellation fails
        """
        if not task:
            logger.warning(f"Task {task.task_id} not found")
            return task

        lfm = LogFileManager(task.log_file, limit=1000, logger=logger)
        try:
            await self.job_manager.cancel_all_jobs(task.get_job_ids())
            lfm.info(f"Successfully cancelled all jobs for task {task.task_id}")
            # Cancel operations via gateway API
            session_id = task.get_session_id()
            operation_ids = task.get_operation_ids()
            if session_id and operation_ids:
                for operation_id in operation_ids:
                    try:
                        await self.sql_gateway_client.operations.cancel_operation.asyncio_detailed(session_handle=session_id, operation_handle=operation_id)
                    except Exception as e:
                        lfm.error(f"Failed to cancel operation {operation_id}: {str(e)}")
            lfm.info(f"Successfully cancelled all operations for task {task.task_id}")
            return task
        except FlinkSqlGatewayNotFoundException:
            lfm.warning(f"Session or operation not found for task {task.task_id}")
        except Exception as e:
            lfm.error(f"Failed to cancel task {task.task_id}: {str(e)}")
        return await self.fetch_task_status(task)

    async def shutdown(self):
        """Shutdown the runner, cancel all tasks and clean up resources."""
        logger.info("Shutting down Flink SQL Runner")

        # Cancel all running tasks
        running_tasks = [task_id for task_id, task in self.tasks.items() if task.status in [TaskStatus.RUNNING, TaskStatus.PENDING]]

        for task_id in running_tasks:
            lfm = LogFileManager(self.tasks[task_id].log_file, limit=1000, logger=logger)
            try:
                logger.info(f"Cancelling task {task_id} during shutdown")
                updated_task = await self.cancel(self.tasks[task_id], force=True)
                # Update our local tasks dict with the updated task
                self.tasks[task_id] = updated_task
            except Exception as e:
                lfm.error(f"Error cancelling task {task_id} during shutdown: {str(e)}")
        # Clean up resources
        try:
            self.resource_manager.cleanup()
            logger.info("Resource manager cleanup completed")
        except Exception as e:
            logger.error(f"Error cleaning up resources: {str(e)}")

    def _create_session_properties(self, task: FlinkSQLTask, resources: FlinkResourcesResult) -> Dict[str, str]:
        """
        Create session properties for the Flink SQL Gateway.

        Args:
            task: The task instance
            resources: Processed resources

        Returns:
            Dictionary of session properties
        """
        properties = {}

        # Add jar paths
        if resources.jar_paths:
            jar_paths = ";".join(resources.jar_paths)
            properties["pipeline.jars"] = jar_paths

        # Add classpath jars
        if resources.classpath_jars:
            classpath_jars = ";".join(resources.classpath_jars)
            properties["pipeline.classpaths"] = classpath_jars

        # Set parallelism
        properties["parallelism.default"] = str(task.parallelism)

        # Add execution mode (we're using streaming for SQL Gateway)
        properties["execution.runtime-mode"] = "streaming"

        # Set pipeline name
        properties["pipeline.name"] = task.pipeline_name

        return properties

    async def fetch_task_status(self, task: FlinkSQLTask) -> FlinkSQLTask:
        """
        Fetches the latest status of a Flink SQL task.

        Args:
            task: The task instance

        Returns:
            An updated task instance with the latest status, result_summary, error_info, and execution_details

        Raises:
            TaskExecutionError: If fetching status fails
        """
        if not task:
            logger.warning(f"Task {task.task_id} not found")
            return None

        if task.all_jobs_finished():
            return task

        lfm = LogFileManager(task.log_file, limit=1000, logger=logger)
        session_id = task.get_session_id()
        operation_ids = task.get_operation_ids()
        job_ids = task.get_job_ids()

        if not job_ids and not operation_ids:
            # if task status is terminal, update all_jobs_finished to True
            if task.status.is_terminal():
                task.result_summary["all_jobs_finished"] = True
            return task

        if job_ids and self.job_manager:
            # Use Flink job statuses as the source of truth
            try:
                task = await self._determine_task_status_from_flink_jobs(task, job_ids, lfm)
            except Exception as e:
                lfm.error(f"Error fetching Flink job statuses for task {task.task_id}: {str(e)}")
                # Fall back to session/operation status check
                task = await self._determine_task_status_from_session(task, session_id, operation_ids, lfm)
        else:
            # Fall back to session/operation status check
            task = await self._determine_task_status_from_session(task, session_id, operation_ids, lfm)

        return task

    async def _determine_task_status_from_flink_jobs(self, task: FlinkSQLTask, job_ids: List[str], lfm: LogFileManager) -> FlinkSQLTask:
        """
        Determine task status based on Flink job statuses.

        Logic:
        - If any job is still running/created/restarting -> RUNNING
        - If all jobs are finished -> COMPLETED
        - If all jobs are failed -> FAILED
        - If any job is cancelled -> CANCELLED
        - Mixed states with some failures -> FAILED
        """
        # map of job_id to job execution result
        job_results = {}
        task_statuses: list[TaskStatus] = []
        job_statuses: list[FlinkJobStatus] = []

        # Get previous job results to compare for changes
        previous_job_results = task.result_summary.get("job_results", {})

        # Fetch status for all jobs
        for job_id in job_ids:
            if not job_id:  # Skip None/empty job IDs
                continue

            try:
                job_details = await self.job_manager.get_job_execution_result(job_id)
                if job_details:
                    # Extract status from the execution-result response
                    # job_details is a JobExecutionResult Pydantic model, not a dict
                    job_status_str = (job_details.status or "").upper()

                    # Convert string to FlinkJobStatus enum
                    try:
                        flink_status = FlinkJobStatus(job_status_str)
                    except ValueError:
                        # Handle unknown status by defaulting to RUNNING
                        lfm.warning(f"Unknown Flink job status: {job_status_str}, defaulting to RUNNING")
                        flink_status = FlinkJobStatus.RUNNING

                    # Map to TaskStatus
                    task_status = map_flink_status_to_task_status(flink_status, job_details.raw_response)
                    error_info = None
                    if task_status == TaskStatus.FAILED:
                        error_info = await self.job_manager.get_job_exceptions(job_id)

                    job_results[job_id] = {
                        "status": flink_status.value,
                        "task_status": task_status.value,
                        "error_info": error_info,
                    }
                    task_statuses.append(task_status)
                    job_statuses.append(flink_status)

                    # Only log if status changed from previous check
                    previous_status = previous_job_results.get(job_id, {}).get("status")
                    if previous_status != flink_status.value:
                        lfm.info(f"Job {job_id} status changed: {previous_status or 'UNKNOWN'} -> {flink_status.value} -> {task_status.value}")
                else:
                    lfm.warning(f"Could not fetch details for job {job_id}")
                    # Job not found, assume it completed or was cleaned up
                    job_results[job_id] = {
                        "status": FlinkJobStatus.FINISHED.value,
                        "task_status": TaskStatus.COMPLETED.value,
                    }
                    task_statuses.append(TaskStatus.COMPLETED)
                    job_statuses.append(FlinkJobStatus.FINISHED)
            except Exception as e:
                lfm.error(f"Error fetching status for job {job_id}: {str(e)}")
                # If we can't get status, assume job failed
                job_results[job_id] = {
                    "status": FlinkJobStatus.FAILED.value,
                    "task_status": TaskStatus.FAILED.value,
                }
                task_statuses.append(TaskStatus.FAILED)
                job_statuses.append(FlinkJobStatus.FAILED)

        if not job_results:
            # No job statuses available, keep current status
            return task

        task.result_summary["job_results"] = job_results
        task.result_summary["all_jobs_finished"] = all(status.is_terminal() for status in job_statuses)

        # Apply logic based on task statuses
        # Check for running jobs first (highest priority)
        if any(status == TaskStatus.RUNNING for status in task_statuses):
            task.status = TaskStatus.RUNNING
            return task

        # Check for cancelled jobs
        if any(status == TaskStatus.CANCELLED for status in task_statuses):
            task.status = TaskStatus.CANCELLED
            return task

        # Check if all jobs are completed
        if all(status == TaskStatus.COMPLETED for status in task_statuses):
            task.status = TaskStatus.COMPLETED
            return task

        # Check if any job is failed
        if any(status == TaskStatus.FAILED for status in task_statuses):
            task.status = TaskStatus.FAILED
            return task

        # Default: keep current status if we can't determine a clear state
        lfm.warning(f"Could not determine clear status from job statuses: {[status.value for status in task_statuses]}")
        return task

    async def _fetch_operation_results(self, session_handle: str, operation_handle: str, timeout_secs: int, lfm) -> dict:
        """Fetch results from an operation with polling."""
        import asyncio
        import time

        start_time = time.time()
        results = {"results": [], "job_id": None, "status": None}

        while time.time() - start_time < timeout_secs:
            try:
                # Get operation status
                status_response = await self.sql_gateway_client.operations.get_operation_status.asyncio_detailed(
                    session_handle=session_handle, operation_handle=operation_handle
                )

                if status_response.status_code == 200 and status_response.parsed:
                    status = status_response.parsed.status
                    results["status"] = status

                    if status in ["FINISHED", "ERROR", "CANCELED"]:
                        break

                # Fetch results if available
                try:
                    result_response = await self.sql_gateway_client.operations.fetch_results.asyncio_detailed(
                        session_handle=session_handle, operation_handle=operation_handle, token=0
                    )

                    if result_response.status_code == 200 and result_response.parsed:
                        result_data = result_response.parsed
                        if hasattr(result_data, "data") and result_data.data:
                            # Convert to JSON format similar to pandas DataFrame
                            rows = []
                            if hasattr(result_data, "columns") and result_data.columns:
                                column_names = [col.name for col in result_data.columns]
                                for row_data in result_data.data:
                                    row_dict = {}
                                    for i, value in enumerate(row_data):
                                        if i < len(column_names):
                                            row_dict[column_names[i]] = value
                                    rows.append(row_dict)
                            results["results"] = rows

                        # Extract job ID if present
                        if hasattr(result_data, "job_id") and result_data.job_id:
                            results["job_id"] = result_data.job_id

                except Exception as e:
                    lfm.warning(f"Could not fetch results: {str(e)}")

                await asyncio.sleep(0.5)  # Poll interval

            except Exception as e:
                lfm.error(f"Error polling operation: {str(e)}")
                break

        return results

    async def _determine_task_status_from_session(self, task: FlinkSQLTask, session_id: str, operation_ids: List[str], lfm) -> FlinkSQLTask:
        """
        Fallback method to determine task status from session/operation status.
        """
        if not session_id or not operation_ids:
            lfm.warning(f"No session or operation ID found for task {task.task_id}")
            return task

        try:
            # Check the last operation status
            operation_id = operation_ids[-1]
            try:
                status_response = await self.sql_gateway_client.operations.get_operation_status.asyncio_detailed(
                    session_handle=session_id, operation_handle=operation_id
                )
                if status_response.status_code == 200 and status_response.parsed:
                    status_str = status_response.parsed.status
                    task.status = TaskStatus.from_str(status_str)
                    lfm.info(f"Session operation status for task {task.task_id}: {task.status.value}")
                else:
                    lfm.warning(f"Could not get session operation status for task {task.task_id}")
                    # If we can't get the operation status, it might have been cleaned up
                    if task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                        task.status = TaskStatus.COMPLETED  # Assume completed if operation is gone
            except Exception as e:
                lfm.error(f"Error getting operation status: {str(e)}")
                if task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    task.status = TaskStatus.COMPLETED
        except FlinkSqlGatewayNotFoundException:
            lfm.warning(f"Session or operation not found for task {task.task_id}")
            task.status = TaskStatus.COMPLETED
        except Exception as e:
            lfm.error(f"Error fetching status for task {task.task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
        return task
