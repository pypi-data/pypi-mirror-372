# Flink CDC Pipeline Runner
import asyncio
import os
import re
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

import yaml

from resinkit_api.clients.job_manager.flink_job_manager_client import FlinkJobManager
from resinkit_api.core.config import settings
from resinkit_api.core.logging import get_logger
from resinkit_api.db.models import Task, TaskStatus
from resinkit_api.services.agent.common.log_file_manager import LogFileManager
from resinkit_api.services.agent.data_models import FlinkJobStatus, TaskExecutionError, map_flink_status_to_task_status
from resinkit_api.services.agent.flink.flink_cdc_pipeline_task import FlinkCdcPipelineTask
from resinkit_api.services.agent.flink.flink_resource_manager import FlinkResourceManager, FlinkResourcesResult
from resinkit_api.services.agent.task_base import TaskBase
from resinkit_api.services.agent.task_runner_base import LogEntry, TaskRunnerBase
from resinkit_api.utils.resource_manager import get_resource_manager

logger = get_logger(__name__)


class FlinkCdcPipelineRunner(TaskRunnerBase):
    """Runner for executing Flink CDC pipeline jobs."""

    def __init__(self, job_manager: FlinkJobManager, runtime_env: dict | None = None):
        """
        Initialize the Flink CDC Pipeline Runner.

        Args:
            job_manager: FlinkJobManager instance for job management
            runtime_env: Optional runtime environment configuration
        """
        super().__init__(runtime_env or {})
        self.flink_home = settings.FLINK_HOME
        self.tasks: Dict[str, FlinkCdcPipelineTask] = {}
        self.job_manager = job_manager
        self.resource_manager = FlinkResourceManager()
        self._temp_dirs = []  # Track temporary directories for cleanup

    @classmethod
    def validate_config(cls, task_config: dict) -> None:
        """
        Validates the configuration for running a Flink CDC pipeline.

        Args:
            task_config: The task configuration dictionary

        Raises:
            ValueError: If the configuration is invalid
        """
        try:
            FlinkCdcPipelineTask.validate(task_config)
        except Exception as e:
            raise ValueError(f"Invalid Flink CDC pipeline configuration: {str(e)}")

    def from_dao(self, dao: Task, variables: Dict[str, Any] | None = None) -> FlinkCdcPipelineTask:
        """
        Create a FlinkCdcPipelineTask instance from a Task DAO.

        Args:
            dao: The Task DAO
            variables: Optional variables for template substitution

        Returns:
            The FlinkCdcPipelineTask instance
        """
        return FlinkCdcPipelineTask.from_dao(dao, variables)

    async def submit_task(self, task: FlinkCdcPipelineTask) -> FlinkCdcPipelineTask:
        """
        Submits a Flink CDC pipeline job.

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

            lfm.info(f"Starting Flink CDC Pipeline: {task.name}")

            # Prepare environment variables
            env_vars = await self._prepare_environment(task)

            # Create configuration files
            config_files = await self._prepare_config_files(task, resources)

            # Prepare the command to run
            cmd = await self._build_flink_command(task, config_files, resources)

            # Execute the command
            process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT, env=env_vars)
            task.process = process

            # Read the initial output to capture job submission response
            initial_output = await self._read_initial_output(process, task.log_file, lfm)

            # Extract job ID from the output
            job_id = self._extract_job_id_from_output(initial_output)

            if job_id:
                lfm.info(f"Successfully submitted Flink CDC pipeline with Job ID: {job_id}")
                task.result_summary["job_id"] = job_id
                task.result_summary["job_ids"] = [job_id]
                task.result["flink_job_id"] = job_id
            else:
                error_msg = "Could not extract Job ID from submission output"
                lfm.warning(error_msg)
                task.status = TaskStatus.FAILED
                task.error_info = {"error": error_msg, "error_type": error_msg, "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}

            # Update execution_details with important execution information
            task.execution_details = {"log_file": task.log_file, "command": " ".join(cmd), "job_ids": [job_id] if job_id else [], "process_id": process.pid}
            lfm.info(f"Flink CDC pipeline submitted successfully, name: {task.name}, id: {task.task_id}")
            return task

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_info = {"error": str(e), "error_type": e.__class__.__name__, "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")}
            error_msg = f"Unexpected error while submitting Flink CDC pipeline: {str(e)}"
            lfm.error(error_msg)
            logger.error(error_msg, exc_info=True)
            return task

    def get_status(self, task: TaskBase) -> TaskStatus:
        """
        Gets the status of a submitted Flink CDC pipeline job.

        Args:
            task: The task instance

        Returns:
            The task status
        """
        if not task:
            return TaskStatus.UNKNOWN
        return task.status

    def get_result(self, task: FlinkCdcPipelineTask) -> Optional[Any]:
        """
        Gets the result of a completed Flink CDC pipeline job.

        Args:
            task: The task instance

        Returns:
            The task result
        """
        if not task:
            return None
        return task.result

    def get_log_summary(self, task: FlinkCdcPipelineTask, level: str = "INFO") -> List[LogEntry]:
        """
        Gets a summary of logs for a Flink CDC pipeline job.

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

    async def cancel(self, task: FlinkCdcPipelineTask, force: bool = False) -> FlinkCdcPipelineTask:
        """
        Cancels a running Flink CDC pipeline job.

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

        if task.status not in [TaskStatus.RUNNING, TaskStatus.PENDING]:
            lfm.info(f"Task {task.task_id} is not running, current status: {task.status.value}")
            return task

        task.status = TaskStatus.CANCELLING

        try:
            # Cancel via Flink job manager if we have job ID
            job_ids = task.get_job_ids()
            if job_ids and self.job_manager:
                lfm.info(f"Cancelling Flink jobs: {job_ids}")
                await self.job_manager.cancel_all_jobs(job_ids)
                lfm.info(f"Successfully cancelled Flink jobs for task {task.task_id}")

            # If we have a process, terminate it
            if task.process:
                if force:
                    task.process.kill()
                else:
                    task.process.terminate()

                # Wait for the process to terminate
                try:
                    await asyncio.wait_for(task.process.wait(), timeout=30.0)
                except asyncio.TimeoutError:
                    lfm.warning(f"Timeout waiting for task {task.task_id} to terminate, forcing kill")
                    task.process.kill()

            task.status = TaskStatus.CANCELLED
            lfm.info(f"Successfully cancelled task {task.task_id}")
            return task

        except Exception as e:
            lfm.error(f"Failed to cancel task {task.task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.result = {"error": f"Cancel failed: {str(e)}"}
            raise TaskExecutionError(f"Failed to cancel task: {str(e)}")

    async def shutdown(self):
        """Shutdown the runner, cancel all tasks and clean up resources."""
        logger.info("Shutting down Flink CDC Pipeline Runner")

        # Cancel all running tasks
        running_tasks = [task_id for task_id, task in self.tasks.items() if task.status in [TaskStatus.RUNNING, TaskStatus.PENDING]]

        for task_id in running_tasks:
            try:
                logger.info(f"Cancelling task {task_id} during shutdown")
                updated_task = await self.cancel(self.tasks[task_id], force=True)
                # Update our local tasks dict with the updated task
                self.tasks[task_id] = updated_task
            except Exception as e:
                logger.error(f"Error cancelling task {task_id} during shutdown: {str(e)}")

        # Clean up resources
        self._cleanup_resources()

    async def fetch_task_status(self, task: FlinkCdcPipelineTask) -> FlinkCdcPipelineTask:
        """
        Fetches the latest status of a Flink CDC pipeline task.

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
        job_ids = task.get_job_ids()

        # If we have job IDs, use Flink job manager as source of truth
        if job_ids and self.job_manager:
            try:
                task = await self._determine_task_status_from_flink_jobs(task, job_ids, lfm)
            except Exception as e:
                lfm.error(f"Error fetching Flink job statuses for task {task.task_id}: {str(e)}")
                # Fall back to process status check
                task = await self._determine_task_status_from_process(task, lfm)
        else:
            # NO job IDs, let's set all_job_finished to True
            task.result_summary["all_jobs_finished"] = True
            # Fall back to process status check
            task = await self._determine_task_status_from_process(task, lfm)

        return task

    async def _determine_task_status_from_flink_jobs(self, task: FlinkCdcPipelineTask, job_ids: List[str], lfm: LogFileManager) -> FlinkCdcPipelineTask:
        """
        Determine task status based on Flink job statuses.

        Logic:
        - If any job is still running/created/restarting -> RUNNING
        - If all jobs are finished -> COMPLETED
        - If all jobs are failed -> FAILED
        - If any job is cancelled -> CANCELLED
        - Mixed states with some failures -> FAILED
        """
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
                    job_status_str = (job_details.application_status or job_details.status or "").upper()

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

    async def _determine_task_status_from_process(self, task: FlinkCdcPipelineTask, lfm: LogFileManager) -> FlinkCdcPipelineTask:
        """
        Fallback method to determine task status from process status.
        """
        if not task.process:
            lfm.warning(f"Task {task.task_id} has no process")
            # reaching here means the status is TBD, but process has been killed, let's set status to COMPLETED
            task.status = TaskStatus.COMPLETED
            return task

        # Check if the process is still running
        if task.process.returncode is None:
            # Process is still running
            try:
                # Try to check for a Flink job ID if we don't have one yet
                if not task.get_job_id():
                    flink_job_id = await self._extract_flink_job_id(task.log_file)
                    if flink_job_id:
                        lfm.info(f"Found Flink job ID for task {task.task_id}: {flink_job_id}")
                        task.result["flink_job_id"] = flink_job_id
                        if task.result_summary:
                            task.result_summary["job_id"] = flink_job_id
                            task.result_summary["job_ids"] = [flink_job_id]
                        if task.execution_details:
                            task.execution_details["job_ids"] = [flink_job_id]

                task.status = TaskStatus.RUNNING
            except Exception as e:
                lfm.error(f"Error updating task {task.task_id} status: {str(e)}")
        else:
            # Process has exited
            exit_code = task.process.returncode
            lfm.info(f"Task {task.task_id} process exited with code {exit_code}")

            if exit_code == 0:
                task.status = TaskStatus.COMPLETED
                # Update result_summary for successful completion
                task.result_summary = task.result_summary or {}
                task.result_summary.update({"success": True, "exit_code": exit_code, "job_id": task.get_job_id()})
            else:
                task.status = TaskStatus.FAILED
                error_message = f"Process exited with code {exit_code}"
                task.result["error"] = error_message
                # Update error_info for process failure
                task.error_info = {
                    "error": error_message,
                    "error_type": "ProcessExitError",
                    "exit_code": exit_code,
                    "timestamp": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S"),
                }

        return task

    def _cleanup_resources(self):
        """Clean up all temporary resources."""
        # Clean up resource manager
        try:
            self.resource_manager.cleanup()
            logger.info("Resource manager cleanup completed")
        except Exception as e:
            logger.error(f"Error cleaning up resource manager: {str(e)}")

        # Clean up temporary directories
        for temp_dir in self._temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    from pathlib import Path

                    get_resource_manager().cleanup_dir(Path(temp_dir))
                    logger.info(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    logger.error(f"Failed to clean up temporary directory {temp_dir}: {str(e)}")

    async def _prepare_environment(self, task: FlinkCdcPipelineTask) -> Dict[str, str]:
        """Prepares the environment variables for running a Flink CDC pipeline."""
        env = os.environ.copy()

        # Add FLINK_HOME if not already set
        if "FLINK_HOME" not in env:
            env["FLINK_HOME"] = self.flink_home

        # Add any additional environment variables from the configuration
        if task.runtime and "environment" in task.runtime:
            for key, value in task.runtime.get("environment", {}).items():
                if isinstance(value, str):
                    env[key.upper()] = value

        return env

    async def _prepare_config_files(self, task: FlinkCdcPipelineTask, resources: FlinkResourcesResult) -> Dict[str, str]:
        """Prepares configuration files needed for the Flink CDC pipeline."""
        config_files = {}

        # Create a temporary directory for configuration files
        temp_dir = str(get_resource_manager().create_temp_dir("flink_cdc_"))
        self._temp_dirs.append(temp_dir)  # Track for cleanup

        # Create pipeline configuration file
        if task.job:
            pipeline_config_path = os.path.join(temp_dir, "pipeline-config.yaml")
            with open(pipeline_config_path, "w") as f:
                yaml.dump(task.job, f, default_flow_style=False, sort_keys=False)
            config_files["pipeline_config"] = pipeline_config_path

        return config_files

    async def _build_flink_command(self, task: FlinkCdcPipelineTask, config_files: Dict[str, str], resources: FlinkResourcesResult) -> List[str]:
        """Builds the command to run the Flink CDC pipeline."""
        # Base command using flink-cdc.sh
        cmd = [f"{settings.FLINK_CDC_HOME}/bin/flink-cdc.sh"]

        # Add classpath jars if any
        if resources.classpath_jars:
            classpath = ":".join(resources.classpath_jars)
            # Add to existing CLASSPATH if it exists
            if "CLASSPATH" in os.environ:
                classpath = f"{os.environ['CLASSPATH']}:{classpath}"
            os.environ["CLASSPATH"] = classpath
            logger.info(f"Added to CLASSPATH: {classpath}")

        # Add savepoint path if specified
        if task.runtime and "savepoint_path" in task.runtime:
            savepoint_path = task.runtime["savepoint_path"]
            if savepoint_path:
                cmd.extend(["--from-savepoint", savepoint_path])

                # Add allow-non-restored-state flag if specified
                if task.runtime.get("allow_non_restored_state", False):
                    cmd.append("--allow-nonRestored-state")

        # Add claim-mode if specified
        if task.runtime and "claim_mode" in task.runtime:
            claim_mode = task.runtime["claim_mode"]
            cmd.extend(["--claim-mode", claim_mode])

        # Add target if specified
        if task.runtime and "target" in task.runtime:
            target = task.runtime["target"]
            cmd.extend(["--target", target])

        # Add use-mini-cluster flag if specified
        if task.runtime and task.runtime.get("use_mini_cluster", False):
            cmd.append("--use-mini-cluster")

        # Add global config if specified
        if task.runtime and "global_config" in task.runtime:
            global_config = task.runtime["global_config"]
            cmd.extend(["--global-config", global_config])

        # Finally, add the pipeline configuration file path
        if "pipeline_config" in config_files:
            cmd.append(config_files["pipeline_config"])

        # Add individual jar files to command with --jar option
        for jar_path in resources.jar_paths:
            cmd.extend(["--jar", jar_path])

        logger.info(f"Flink CDC command: {' '.join(cmd)}")
        return cmd

    async def _read_initial_output(self, process: asyncio.subprocess.Process, log_file: str, lfm: LogFileManager) -> str:
        """Read initial output from the process to capture job submission response."""
        output_lines = []

        try:
            # Create log file if it doesn't exist
            with open(log_file, "a") as f:
                f.write(f"=== Flink CDC Pipeline Job Started at {datetime.now(UTC).isoformat()} ===\n")

            # Read initial output for a limited time to capture submission response
            timeout = 30  # 30 seconds to capture job submission
            start_time = asyncio.get_event_loop().time()

            while True:
                current_time = asyncio.get_event_loop().time()
                if current_time - start_time > timeout:
                    break

                try:
                    line_bytes = await asyncio.wait_for(process.stdout.readline(), timeout=1.0)
                    if not line_bytes:
                        break

                    line = line_bytes.decode("utf-8").strip()
                    if line:
                        output_lines.append(line)
                        lfm.info(line)

                        # Write to log file immediately
                        with open(log_file, "a") as f:
                            f.write(f"{line}\n")

                        # Check if we've seen the job submission response
                        if "Job ID:" in line or "Pipeline has been submitted" in line:
                            # Continue reading for a bit more to capture complete response
                            continue

                except asyncio.TimeoutError:
                    # No more output available, check if process is still alive
                    if process.returncode is not None:
                        break
                    continue
                except Exception as e:
                    lfm.error(f"Error reading process output: {str(e)}")
                    break

        except Exception as e:
            lfm.error(f"Error setting up output reading: {str(e)}")

        return "\n".join(output_lines)

    def _extract_job_id_from_output(self, output: str) -> Optional[str]:
        """
        Extract Flink job ID from the command output.
        Expected output format:
        ```
        Pipeline has been submitted to cluster.
        Job ID: ae30f4580f1918bebf16752d4963dc54
        Job Description: Sync MySQL Database to Doris
        ```
        """
        if not output:
            return None

        try:
            # Look for job ID pattern in output
            job_id_match = re.search(r"Job ID:\s*([a-f0-9]+)", output, re.IGNORECASE)
            if job_id_match:
                return job_id_match.group(1)

            # Alternative pattern
            job_id_match = re.search(r"JobID\s*([a-f0-9]+)", output, re.IGNORECASE)
            if job_id_match:
                return job_id_match.group(1)

            return None
        except Exception as e:
            logger.error(f"Failed to extract job ID from output: {str(e)}")
            return None

    async def _extract_flink_job_id(self, log_file_path: str) -> Optional[str]:
        """
        Extracts the Flink job ID from the log file.
        Returns None if no job ID could be found.
        """
        if not os.path.exists(log_file_path):
            return None

        try:
            with open(log_file_path, "r") as f:
                log_content = f.read()

            return self._extract_job_id_from_output(log_content)
        except Exception as e:
            logger.error(f"Failed to extract Flink job ID from log file: {str(e)}")
            return None
