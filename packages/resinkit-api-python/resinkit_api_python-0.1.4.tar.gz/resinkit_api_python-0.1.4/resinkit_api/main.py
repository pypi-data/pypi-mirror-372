from fastapi.middleware.cors import CORSMiddleware

from resinkit_api.api.agent import router as agent_router
from resinkit_api.api.flink_api import router as flink_router
from resinkit_api.api.health import router as health_router
from resinkit_api.api.pat import router as authorization_router
from resinkit_api.apps import get_fastapi
from resinkit_api.core.logging import get_logger

logger = get_logger(__name__)

app = get_fastapi()


# Add the security scheme to the OpenAPI components
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include the Flink router with the prefix and dependencies
app.include_router(flink_router)

# Include the health router
app.include_router(health_router)

# Include the authorization router
app.include_router(authorization_router)

# Include the agent router
app.include_router(agent_router)

# # Mount MCP endpoints for agent API

# app.mount("/mcp", get_mcp().http_app())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8602)
