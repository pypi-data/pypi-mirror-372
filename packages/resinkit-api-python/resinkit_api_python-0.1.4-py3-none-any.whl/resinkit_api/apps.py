import contextlib
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastmcp import FastMCP
from fastmcp.server.middleware.logging import LoggingMiddleware, StructuredLoggingMiddleware
from typing_extensions import Annotated

from resinkit_api.core.config import settings
from resinkit_api.core.logging import get_logger
from resinkit_api.services.agent import shutdown_agent_service, startup_agent_service

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI application")

    # Start agent service (includes TaskTiq monitor if enabled)
    await startup_agent_service()
    FastAPICache.init(InMemoryBackend(), prefix="resinkit-api")

    yield

    logger.info("Shutting down FastAPI application")

    # Shutdown agent service
    await shutdown_agent_service()


async def verify_auth(x_resinkit_api_token: Annotated[str, Header()]):
    """Auth verification function for MCP endpoints"""
    if not x_resinkit_api_token:
        raise HTTPException(status_code=401, detail="X-ResinKit-Api-Token header required for MCP access")
    return x_resinkit_api_token


_mcp = None


def get_mcp() -> FastMCP:
    global _mcp
    if _mcp is None:
        # Configure FastAPI-MCP with authentication
        _mcp = FastMCP("Resinkit Agent MCP")
        _mcp.add_middleware(
            StructuredLoggingMiddleware(logger=logger, include_payloads=True)
            if settings.LOG_JSON_FORMAT
            else LoggingMiddleware(logger=logger, include_payloads=True)
        )
    return _mcp


_app = None


def get_fastapi() -> FastAPI:
    global _app
    if _app is None:
        mcp = get_mcp()
        mcp_app = mcp.http_app("/mcp")

        # Create a combined lifespan to manage both session managers
        @asynccontextmanager
        async def combined_lifespan(app: FastAPI):
            async with contextlib.AsyncExitStack() as stack:
                await stack.enter_async_context(mcp_app.lifespan(app))
                await stack.enter_async_context(lifespan(app))
                yield

        _app = FastAPI(
            title="Resinkit API",
            description="Service for interacting with Resinkit",
            version="0.1.0",
            contact={
                "name": "Resinkit",
                "url": "https://resink.ai",
                "email": "support@resink.ai",
            },
            lifespan=combined_lifespan,
        )
        _app.mount("/mcp-server", mcp_app)
    return _app
