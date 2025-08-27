import asyncio
import copy
from datetime import datetime
from typing import Any, Dict, List, Optional

from resinkit_api.core.logging import get_logger
from resinkit_api.db.models import Task, TaskStatus
from resinkit_api.services.agent.task_base import TaskBase
from resinkit_api.utils.resource_manager import get_resource_manager

logger = get_logger(__name__)


class FlinkCdcPipelineTask(TaskBase):
    """A task class for running Flink CDC pipeline jobs."""

    def __init__(
        self,
        task_id: str,
        name: str,
        description: str = "",
        connection_timeout_seconds: int = 30,
        task_timeout_seconds: int = 3600,
        created_at: datetime = None,
        status: TaskStatus = None,
        priority: int = 0,
        updated_at: datetime = None,
        started_at: datetime = None,
        finished_at: datetime = None,
        expires_at: datetime = None,
        created_by: str = None,
        notification_config: Dict[str, Any] = None,
        tags: List[str] = None,
        active: bool = True,
        job: Dict[str, Any] = None,
        runtime: Dict[str, Any] = None,
        resources: Dict[str, Any] = None,
        pipeline_name: str = None,
        error_info: Dict[str, Any] = None,
        result_summary: Dict[str, Any] = None,
        execution_details: Dict[str, Any] = None,
        progress_details: Dict[str, Any] = None,
    ):
        super().__init__(
            task_type="flink_cdc_pipeline",
            name=name,
            description=description,
            connection_timeout_seconds=connection_timeout_seconds,
            task_timeout_seconds=task_timeout_seconds,
            task_id=task_id,
            created_at=created_at,
            status=status,
            priority=priority,
            updated_at=updated_at,
            started_at=started_at,
            finished_at=finished_at,
            expires_at=expires_at,
            created_by=created_by,
            notification_config=notification_config,
            tags=tags,
            active=active,
            error_info=error_info,
            result_summary=result_summary,
            execution_details=execution_details,
            progress_details=progress_details,
        )
        self.process: Optional[asyncio.subprocess.Process] = None
        self.log_file = str(get_resource_manager().create_file_path(f"flink_cdc_{self.task_id}.log", "logs"))
        self.result: Dict[str, Any] = {}
        self.job = job or {}
        self.runtime = runtime or {}
        self.resources = resources or {}
        self.pipeline_name = pipeline_name or name

    @classmethod
    def from_dao(cls, task_dao: Task, variables: Dict[str, Any] | None = None) -> "FlinkCdcPipelineTask":
        """
        Create a FlinkCdcPipelineTask instance from a Task DAO.

        Args:
            task_dao: The Task DAO
            variables: Optional variables for template substitution

        Returns:
            The FlinkCdcPipelineTask instance
        """
        # Get submitted configs and apply variable substitution if needed
        config = task_dao.submitted_configs or {}
        if variables and config:
            config = TaskBase.render_with_variables(config, variables)

        connection_timeout_seconds = config.get("connection_timeout_seconds", 30)
        # recalculate task timeout seconds based on expires_at
        task_timeout_seconds = (task_dao.expires_at - task_dao.created_at).total_seconds() if task_dao.expires_at else 3600

        pipeline_config = config.get("job", {}).get("pipeline") or {}

        return cls(
            task_id=task_dao.task_id,
            name=task_dao.task_name,
            description=task_dao.description,
            connection_timeout_seconds=connection_timeout_seconds,
            task_timeout_seconds=task_timeout_seconds,
            created_at=task_dao.created_at,
            status=task_dao.status,
            priority=task_dao.priority,
            updated_at=task_dao.updated_at,
            started_at=task_dao.started_at,
            finished_at=task_dao.finished_at,
            expires_at=task_dao.expires_at,
            created_by=task_dao.created_by,
            notification_config=copy.deepcopy(task_dao.notification_config) if task_dao.notification_config else None,
            tags=copy.deepcopy(task_dao.tags) if task_dao.tags else None,
            active=task_dao.active,
            job=config.get("job", {}),
            runtime=config.get("runtime", {}),
            resources=config.get("resources", {}),
            pipeline_name=pipeline_config.get("name", task_dao.task_name),
            error_info=copy.deepcopy(task_dao.error_info) if task_dao.error_info else None,
            result_summary=copy.deepcopy(task_dao.result_summary) if task_dao.result_summary else None,
            execution_details=copy.deepcopy(task_dao.execution_details) if task_dao.execution_details else None,
            progress_details=copy.deepcopy(task_dao.progress_details) if task_dao.progress_details else None,
        )

    @classmethod
    def validate(cls, config: dict) -> None:
        """
        Validate the FlinkCdcPipelineTask configuration dictionary.

        Args:
            config: The configuration dictionary to validate

        Raises:
            ValueError: If the configuration is invalid
        """
        # Validate base configuration
        TaskBase.validate(config)

        # Check for required job configuration
        job_config = config.get("job")
        if not job_config:
            raise ValueError("Missing required 'job' configuration")

        if not isinstance(job_config, dict):
            raise ValueError("Job configuration must be a dictionary")

        # Validate runtime configuration if present
        runtime = config.get("runtime")
        if runtime is not None and not isinstance(runtime, dict):
            raise ValueError("Runtime configuration must be a dictionary")

        # Validate resources configuration if present
        resources = config.get("resources")
        if resources is not None and not isinstance(resources, dict):
            raise ValueError("Resources configuration must be a dictionary")

        # Validate timeout
        if config.get("task_timeout_seconds", 3600) <= 0:
            raise ValueError("Task timeout must be a positive integer")

        # Validate resources if present
        if resources:
            cls._validate_resources(resources)

    @staticmethod
    def _validate_resources(resources: dict) -> None:
        """Validate resources configuration."""
        if "flink_jars" in resources:
            jars = resources["flink_jars"]
            if not isinstance(jars, list):
                raise ValueError("flink_jars must be a list")
            for jar in jars:
                if not isinstance(jar, dict):
                    raise ValueError("Each jar in flink_jars must be a dictionary")
                if "name" not in jar:
                    raise ValueError("Each jar in flink_jars must have a name")
                if "location" not in jar and "source" not in jar:
                    raise ValueError("Each jar in flink_jars must have either a location or a source")

    def get_job_ids(self) -> List[str]:
        """Get the list of Flink job IDs associated with this task."""
        job_ids = []

        # Check if we have a job_id in result_summary
        if self.result_summary and self.result_summary.get("job_id"):
            job_ids.append(self.result_summary["job_id"])

        # Check if we have job_ids in result_summary (for multiple jobs)
        if self.result_summary and self.result_summary.get("job_ids"):
            job_ids.extend(self.result_summary["job_ids"])

        # Check if we have a job_id in result dict
        if self.result and self.result.get("flink_job_id"):
            job_ids.append(self.result["flink_job_id"])

        # Check execution_details
        if self.execution_details and self.execution_details.get("job_ids"):
            job_ids.extend(self.execution_details["job_ids"])

        # Remove duplicates and None values
        return list(filter(None, list(set(job_ids))))

    def get_job_id(self) -> str | None:
        """Get the primary Flink job ID associated with this task."""
        job_ids = self.get_job_ids()
        return job_ids[0] if job_ids else None

    def all_jobs_finished(self) -> bool:
        """Check if all jobs have finished (based on result_summary)."""
        return self.result_summary.get("all_jobs_finished", False) if self.result_summary else False
