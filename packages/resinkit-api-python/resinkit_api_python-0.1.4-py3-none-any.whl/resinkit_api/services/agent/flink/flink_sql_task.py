import copy
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from resinkit_api.core.logging import get_logger
from resinkit_api.db.models import Task, TaskStatus
from resinkit_api.db.variables_crud import get_all_variables_decrypted
from resinkit_api.services.agent.task_base import TaskBase
from resinkit_api.utils.misc_utils import render_with_string_template
from resinkit_api.utils.resource_manager import get_resource_manager

logger = get_logger(__name__)


class FlinkSQLTask(TaskBase):
    """A task class for running Flink SQL jobs via the SQL Gateway."""

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
        sql_statements: List[str] = None,
        pipeline_name: str = None,
        parallelism: int = 1,
        resources: Dict[str, Any] = None,
        error_info: Dict[str, Any] = None,
        result_summary: Dict[str, Any] = None,
        execution_details: Dict[str, Any] = None,
        progress_details: Dict[str, Any] = None,
    ):
        super().__init__(
            task_type="flink_sql",
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
        self.sql_statements = sql_statements or []
        self.pipeline_name = pipeline_name or name
        self.parallelism = parallelism
        self.resources = resources or {}
        self.result: Dict[str, Any] = {}
        self.log_file = str(get_resource_manager().create_file_path(f"{self.task_id}.log", "logs"))

    @classmethod
    def from_dao(cls, task_dao: Task, variables: Dict[str, Any] | None = None) -> "FlinkSQLTask":
        # Get submitted configs and apply variable substitution if needed
        config = task_dao.submitted_configs or {}
        if variables and config:
            config = TaskBase.render_with_variables(config, variables)

        job_config = config.get("job", {})
        connection_timeout_seconds = config.get("connection_timeout_seconds", 30)
        # recalculate task timeout seconds based on expires_at
        task_timeout_seconds = (task_dao.expires_at - task_dao.created_at).total_seconds() if task_dao.expires_at else 3600
        # TODO: pipeline configs are not used yet
        pipeline_config = job_config.get("pipeline", {})

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
            sql_statements=cls._parse_sql_statements(job_config.get("sql", "")),
            pipeline_name=pipeline_config.get("name", task_dao.task_name),
            parallelism=pipeline_config.get("parallelism", 1),
            resources=config.get("resources", {}),
            error_info=copy.deepcopy(task_dao.error_info) if task_dao.error_info else None,
            result_summary=copy.deepcopy(task_dao.result_summary) if task_dao.result_summary else None,
            execution_details=copy.deepcopy(task_dao.execution_details) if task_dao.execution_details else None,
            progress_details=copy.deepcopy(task_dao.progress_details) if task_dao.progress_details else None,
        )

    @staticmethod
    def _parse_sql_statements(sql_text: str) -> List[str]:
        """
        Parse the SQL text into individual SQL statements.

        Args:
            sql_text: The SQL text from the configuration

        Returns:
            A list of individual SQL statements
        """
        if not sql_text:
            return []

        # Split by semicolons, but handle semicolons within quotes/strings
        statements = []
        current_statement = []
        in_string = False

        for line in sql_text.splitlines():
            line = line.strip()
            if not line or line.startswith("--"):  # Skip empty lines and comments
                continue

            current_statement.append(line)

            # Check if this line contains a complete statement
            if line.rstrip().endswith(";") and not in_string:
                statements.append("\n".join(current_statement))
                current_statement = []

        # Add the last statement if there's any remaining
        if current_statement:
            statements.append("\n".join(current_statement))

        return statements

    @staticmethod
    async def _parse_sql_statements_with_variables(sql_text: str, db: Session) -> List[str]:
        """
        Parse the SQL text into individual SQL statements with variable substitution.

        Args:
            sql_text: The SQL text from the configuration
            db: Database session for variable resolution

        Returns:
            A list of individual SQL statements with variables resolved
        """
        if not sql_text:
            return []

        # Apply variable substitution
        variables = await get_all_variables_decrypted(db)
        sql_text = render_with_string_template(sql_text, variables)

        # Use the existing parsing logic
        return FlinkSQLTask._parse_sql_statements(sql_text)

    @classmethod
    def validate(cls, config: dict) -> None:
        """
        Validate the FlinkSQLTask configuration dictionary.
        Raises:
            ValueError: If the configuration is invalid
        """
        # Extract SQL statements from nested job.sql
        job = config.get("job", {})
        sql_text = job.get("sql", "")
        sql_statements = cls._parse_sql_statements(sql_text)
        if not sql_statements:
            raise ValueError("No SQL statements found in the task configuration (expected under job.sql)")

        # Extract parallelism from job.pipeline.parallelism
        pipeline = job.get("pipeline", {})
        parallelism = pipeline.get("parallelism", 1)
        if parallelism <= 0:
            raise ValueError("Parallelism must be a positive integer (expected under job.pipeline.parallelism)")

        # Extract task_timeout_seconds from top-level
        if config.get("task_timeout_seconds", 3600) <= 0:
            raise ValueError("Task timeout must be a positive integer")

        # Extract resources from top-level
        resources = config.get("resources", {})
        if resources:
            cls._validate_resources(resources)

    @staticmethod
    def _validate_resources(resources: dict) -> None:
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

    def get_operation_ids(self) -> List[str]:
        return self.execution_details.get("operation_ids", [])

    def get_session_id(self) -> str | None:
        return self.execution_details.get("session_id")

    def get_job_ids(self) -> List[str]:
        return self.execution_details.get("job_ids", [])

    def all_jobs_finished(self) -> bool:
        return self.result_summary.get("all_jobs_finished", False)
