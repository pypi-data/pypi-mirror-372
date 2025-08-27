import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from starlette.requests import Request

from resinkit_api.api.models.models_flink import (
    CloseSessionResponse,
    ExecuteSQLRequest,
    HeartbeatResponse,
    OpenSessionRequest,
    OpenSessionResponse,
)
from resinkit_api.core.logging import get_logger
from resinkit_api.db.database import get_db
from resinkit_api.services.flink_session_service import FlinkSessionService
from resinkit_api.services.flink_sql_execution_service import FlinkSQLExecutionService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/flink", tags=["flink"])

# Create a singleton instance of FlinkSessionService
_session_service_instance: Optional[FlinkSessionService] = None


def get_session_service() -> FlinkSessionService:
    """Dependency to get Flink session service singleton."""
    global _session_service_instance
    if _session_service_instance is None:
        _session_service_instance = FlinkSessionService()
    return _session_service_instance


def get_sql_execution_service(session_service: FlinkSessionService = Depends(get_session_service)) -> FlinkSQLExecutionService:
    """Dependency to get Flink SQL execution service."""
    return FlinkSQLExecutionService(session_service)


@router.post(
    "/sessions",
    response_model=OpenSessionResponse,
    summary="Open a new Flink session",
    description="Creates a new Flink SQL Gateway session with optional properties and name",
)
async def open_session(request: OpenSessionRequest, session_service: FlinkSessionService = Depends(get_session_service)) -> OpenSessionResponse:
    """Open a new Flink session."""
    try:
        session_id = await session_service.open_session(properties=request.properties, session_name=request.session_name)
        return OpenSessionResponse(session_id=session_id)
    except Exception as e:
        logger.error(f"Failed to open session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to open session: {str(e)}")


@router.delete(
    "/sessions/{session_id}", response_model=CloseSessionResponse, summary="Close a Flink session", description="Closes an existing Flink SQL Gateway session"
)
async def close_session(session_id: str, session_service: FlinkSessionService = Depends(get_session_service)) -> CloseSessionResponse:
    """Close a Flink session."""
    try:
        success = await session_service.close_session(session_id)
        if success:
            return CloseSessionResponse(success=True, message="Session closed successfully")
        else:
            return CloseSessionResponse(success=False, message="Session not found or already closed")
    except Exception as e:
        logger.error(f"Failed to close session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to close session: {str(e)}")


@router.post(
    "/sessions/{session_id}/heartbeat",
    response_model=HeartbeatResponse,
    summary="Send heartbeat to keep session alive",
    description="Sends a heartbeat to the specified session to keep it active",
)
async def heartbeat_session(session_id: str, session_service: FlinkSessionService = Depends(get_session_service)) -> HeartbeatResponse:
    """Send heartbeat to keep session alive."""
    try:
        success = await session_service.heartbeat_session(session_id)
        if success:
            return HeartbeatResponse(success=True, message="Heartbeat sent successfully")
        else:
            return HeartbeatResponse(success=False, message="Session not found or heartbeat failed")
    except Exception as e:
        logger.error(f"Failed to send heartbeat to session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send heartbeat: {str(e)}")


@router.post(
    "/sessions/{session_id}/execute",
    summary="Execute SQL statements with streaming results",
    description="Executes SQL statements in the specified session and streams back results as JSON objects",
)
async def execute_sql_streaming(
    session_id: str,
    request: ExecuteSQLRequest,
    http_request: Request,
    sql_execution_service: FlinkSQLExecutionService = Depends(get_sql_execution_service),
    db: Session = Depends(get_db),
    poll_interval_secs: Optional[float] = 0.1,
    max_poll_secs: Optional[float] = None,
    n_row_limit: Optional[int] = None,
) -> StreamingResponse:
    """
    Execute SQL statements and stream results.

    Args:
        session_id: Session ID
        request: ExecuteSQLRequest
        http_request: HTTP request

    Returns:
        Normal: StreamingResponse with SQL results
        Error:
        - response.meta_data.operation_id = "error"
        - response.fetch_result.data = [[f"Error executing SQL: {e}"]]
    """

    async def generate_results():
        """Generator function for streaming SQL results."""
        try:
            logger.info(f"Starting SQL execution in session {session_id}")

            async for result in sql_execution_service.execute_sql_streaming(
                session_id=session_id,
                sql=request.sql,
                execution_config=request.execution_config,
                execution_timeout=request.execution_timeout,
                poll_interval_secs=poll_interval_secs or 0.1,
                max_poll_secs=max_poll_secs,
                n_row_limit=n_row_limit,
                db=db,
            ):
                # Check if client has disconnected
                if await http_request.is_disconnected():
                    logger.info(f"Client disconnected during SQL execution in session {session_id}")
                    break

                # Convert Pydantic model to JSON and yield
                json_line = result.model_dump_json() + "\n"
                yield json_line

                logger.debug(f"Streamed result for session {session_id}, EOS: {result.fetch_result.eos}")

        except Exception as e:
            # Use compact error message for better readability
            logger.warning(f"Error during SQL execution in session {session_id}: {e}")
            error_response = {
                "meta_data": {"sql": request.sql, "session_id": session_id, "operation_id": "error"},
                "fetch_result": {
                    "columns": [{"name": "error", "logical_type": {"type": "VARCHAR", "nullable": True}, "comment": None}],
                    "data": [[f"Error executing SQL: {e}"]],
                    "eos": True,
                    "job_id": None,
                    "is_query_result": False,
                },
            }
            yield json.dumps(error_response) + "\n"

    return StreamingResponse(
        generate_results(),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/sessions", summary="List all active sessions", description="Returns a list of all active Flink sessions")
async def list_sessions(session_service: FlinkSessionService = Depends(get_session_service)) -> dict:
    """List all active sessions."""
    try:
        sessions = session_service.list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Failed to list sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")
