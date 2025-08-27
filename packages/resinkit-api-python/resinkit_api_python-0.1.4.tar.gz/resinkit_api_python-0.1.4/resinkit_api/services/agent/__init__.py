"""
Agent Service Initialization

This module initializes and exports the components of the agent service.
It creates instances of task runners, registers them with the registry,
and provides a clean API for the rest of the application.
"""

import os
from typing import Optional

from resinkit_api.core.logging import get_logger
from resinkit_api.services import get_service_manager
from resinkit_api.services.agent.flink.flink_cdc_pipeline_runner import FlinkCdcPipelineRunner
from resinkit_api.services.agent.flink.flink_sql_runner import FlinkSQLRunner
from resinkit_api.services.agent.runner_registry import TASK_RUNNER_REGISTRY, get_runner_for_task_type, register_runner
from resinkit_api.services.agent.task_tiq_manager import TaskTiqManager

logger = get_logger(__name__)

# Singleton instances
_flink_cdc_pipeline_runner: Optional[FlinkCdcPipelineRunner] = None
_flink_sql_runner: Optional[FlinkSQLRunner] = None
_task_tiq_manager: Optional[TaskTiqManager] = None
_initialized = False


def get_flink_cdc_pipeline_runner() -> FlinkCdcPipelineRunner:
    global _flink_cdc_pipeline_runner
    if _flink_cdc_pipeline_runner is None:
        _flink_cdc_pipeline_runner = FlinkCdcPipelineRunner(job_manager=get_service_manager().job_manager)
    return _flink_cdc_pipeline_runner


def get_flink_sql_runner() -> FlinkSQLRunner:
    global _flink_sql_runner
    if _flink_sql_runner is None:
        _flink_sql_runner = FlinkSQLRunner(job_manager=get_service_manager().job_manager, sql_gateway_client=get_service_manager().flink_gateway_client)
    return _flink_sql_runner


def get_task_tiq_manager() -> TaskTiqManager:
    """Get the TaskTiqManager singleton instance."""
    global _task_tiq_manager
    if _task_tiq_manager is None:
        _task_tiq_manager = TaskTiqManager()
    return _task_tiq_manager


def get_active_task_manager() -> TaskTiqManager:
    """
    Get the active task manager.

    Returns TaskTiqManager as the only task manager implementation.
    """
    logger.info("Using TaskTiqManager for task execution")
    return get_task_tiq_manager()


def initialize_agent_service() -> None:
    """
    Initialize the agent service components.
    This function registers all task runners and initializes dependencies.
    It's designed to be called only once during application startup.
    """
    global _initialized

    if _initialized:
        logger.info("Agent service already initialized, skipping initialization")
        return

    # [DO NOT REMOVE] Import to activate the annotations
    from resinkit_api.mcp.agent import mcp_data_explorer, mcp_resources, mcp_prompts  # noqa

    # Register predefined runners
    # This will load built-in runner types from the registry module,
    logger.info("Registering task runners")
    # Check if the FlinkCdcPipelineRunner is already registered
    if "flink_cdc_pipeline" in TASK_RUNNER_REGISTRY:
        logger.debug("FlinkCdcPipelineRunner already registered")
    else:
        # Create a new runner with services from the service manager
        register_runner("flink_cdc_pipeline", get_flink_cdc_pipeline_runner())
        register_runner("flink_sql", get_flink_sql_runner())
        logger.info("Registered FlinkCdcPipelineRunner")

    _initialized = True
    logger.info("Agent service initialization complete")


async def startup_agent_service() -> None:
    """
    Startup tasks for the agent service.
    This should be called during FastAPI startup.
    """
    logger.info("Starting up agent service")

    # Initialize the service
    initialize_agent_service()

    # Start expired tasks monitor for TaskTiqManager
    task_manager = get_task_tiq_manager()
    await task_manager.start_expired_tasks_monitor()
    logger.info("Started expired tasks monitor for TaskTiqManager")


async def shutdown_agent_service() -> None:
    """
    Shutdown tasks for the agent service.
    This should be called during FastAPI shutdown.
    """
    logger.info("Shutting down agent service")

    # Stop expired tasks monitor for TaskTiqManager
    if _task_tiq_manager:
        await _task_tiq_manager.stop_expired_tasks_monitor()
        logger.info("Stopped expired tasks monitor for TaskTiqManager")

        # Shutdown TaskIQ components
        from resinkit_api.services.agent.taskiq_broker import shutdown_taskiq

        await shutdown_taskiq()
        logger.info("Shutdown TaskIQ components")


# Initialize the agent service when the module is imported
initialize_agent_service()

# Export the public components
__all__ = [
    "get_runner_for_task_type",
    "register_runner",
    "initialize_agent_service",
    "get_flink_cdc_pipeline_runner",
    "get_task_tiq_manager",
    "get_active_task_manager",
    "startup_agent_service",
    "shutdown_agent_service",
]
