from flink_gateway_api import Client as FlinkGatewayClient

from resinkit_api.clients.job_manager.flink_job_manager_client import FlinkJobManager
from resinkit_api.core.config import settings
from resinkit_api.core.logging import get_logger

logger = get_logger(__name__)


class SvcManager:
    """
    Service manager responsible for creating and managing service instances.
    This provides a central point of access to all services with dependency injection.
    """

    def __init__(self):
        """
        Initialize the service manager with dependencies.

        Args:
            flink_gateway_api_client: Client for Flink Gateway API (if needed).
        """
        logger.debug("Initializing service manager")

        # Initialize Flink Gateway API client
        self._flink_gateway_client = FlinkGatewayClient(
            base_url=settings.FLINK_SQL_GATEWAY_URL,
            raise_on_unexpected_status=True,
        )

        # Initialize services
        self._job_manager_client: "FlinkJobManager" = FlinkJobManager()

    @property
    def job_manager(self) -> "FlinkJobManager":
        return self._job_manager_client

    @property
    def flink_gateway_client(self) -> FlinkGatewayClient:
        return self._flink_gateway_client
