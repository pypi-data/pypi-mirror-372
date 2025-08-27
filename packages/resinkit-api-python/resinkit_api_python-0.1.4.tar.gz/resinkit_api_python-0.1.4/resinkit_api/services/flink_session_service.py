import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator, Dict, Optional

from flink_gateway_api import Client
from flink_gateway_api.api.default import close_session, open_session, trigger_session
from flink_gateway_api.models import OpenSessionRequestBody

from resinkit_api.core.config import settings
from resinkit_api.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class SessionInfo:
    """Information about a Flink session."""

    session_handle: str
    session_name: str
    properties: Dict[str, str]
    client: Client


class FlinkSessionService:
    """Service for managing Flink SQL Gateway sessions."""

    def __init__(self, gateway_url: Optional[str] = None):
        self.gateway_url = gateway_url or settings.FLINK_SQL_GATEWAY_URL
        self.client = Client(
            base_url=self.gateway_url,
            raise_on_unexpected_status=True,
            timeout=10,
        )
        self.sessions: Dict[str, SessionInfo] = {}

    async def open_session(self, properties: Optional[Dict[str, str]] = None, session_name: Optional[str] = None) -> str:
        """
        Open a new Flink session.

        Args:
            properties: Session properties
            session_name: Custom session name

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())

        if session_name is None:
            session_name = f"api_session_{session_id}"

        try:
            # Open session using flink_gateway_api directly
            response = await open_session.asyncio(
                client=self.client, body=OpenSessionRequestBody.from_dict({"properties": properties or {}, "sessionName": session_name})
            )

            session_info = SessionInfo(session_handle=response.session_handle, session_name=session_name, properties=properties or {}, client=self.client)

            self.sessions[session_id] = session_info

            logger.info(f"Opened Flink session {session_id} with handle {response.session_handle}")
            return session_id

        except Exception as e:
            logger.error(f"Failed to open Flink session: {str(e)}")
            raise

    async def close_session(self, session_id: str) -> bool:
        """
        Close a Flink session.

        Args:
            session_id: Session ID

        Returns:
            True if session was closed successfully
        """
        session_info = self.sessions.get(session_id)
        if not session_info:
            logger.warning(f"Session {session_id} not found")
            return False

        try:
            # Close the session using flink_gateway_api
            await close_session.asyncio(session_info.session_handle, client=self.client)
            del self.sessions[session_id]

            logger.info(f"Closed Flink session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to close session {session_id}: {str(e)}")
            return False

    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get a session by ID."""
        return self.sessions.get(session_id)

    async def heartbeat_session(self, session_id: str) -> bool:
        """
        Send heartbeat to keep session alive.

        Args:
            session_id: Session ID

        Returns:
            True if heartbeat was successful
        """
        session_info = self.sessions.get(session_id)
        if not session_info:
            logger.warning(f"Session {session_id} not found for heartbeat")
            return False

        try:
            response = await trigger_session.asyncio_detailed(session_handle=session_info.session_handle, client=self.client)
            success = response.status_code == 200
            if success:
                logger.debug(f"Heartbeat successful for session {session_id}")
            else:
                logger.warning(f"Heartbeat failed for session {session_id}: {response.status_code}")
            return success

        except Exception as e:
            logger.error(f"Heartbeat failed for session {session_id}: {str(e)}")
            return False

    async def cleanup_all_sessions(self) -> None:
        """Clean up all sessions."""
        session_ids = list(self.sessions.keys())
        for session_id in session_ids:
            await self.close_session(session_id)

    def list_sessions(self) -> Dict[str, str]:
        """
        List all active sessions.

        Returns:
            Dict mapping session_id to session_name
        """
        return {session_id: session_info.session_name for session_id, session_info in self.sessions.items()}

    @asynccontextmanager
    async def session_context(
        self, properties: Optional[Dict[str, str]] = None, session_name: Optional[str] = None
    ) -> AsyncGenerator[tuple[str, SessionInfo], None]:
        """
        Context manager for automatic session cleanup.

        Args:
            properties: Session properties
            session_name: Custom session name

        Yields:
            Tuple of (session_id, session_info)
        """
        session_id = await self.open_session(properties, session_name)
        try:
            session_info = self.get_session(session_id)
            yield session_id, session_info
        finally:
            await self.close_session(session_id)
