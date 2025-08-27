import time
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, Header, HTTPException

from resinkit_api.core.config import settings
from resinkit_api.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/pat", tags=["common"])

# Cache for PAT validation results
# Structure: {pat_token: {"result": validation_result, "timestamp": cache_time}}
_pat_cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour cache TTL


def _get_cached_result(pat: str) -> Optional[Dict[str, Any]]:
    """Get cached validation result if it exists and is not expired."""
    if pat not in _pat_cache:
        return None

    cached_entry = _pat_cache[pat]
    if time.time() - cached_entry["timestamp"] > CACHE_TTL_SECONDS:
        # Cache expired, remove it
        del _pat_cache[pat]
        return None

    return cached_entry["result"]


def _cache_result(pat: str, result: Dict[str, Any]) -> None:
    """Cache the validation result for the given PAT."""
    _pat_cache[pat] = {"result": result, "timestamp": time.time()}


@router.get("/validate")
async def validate(x_resinkit_pat: Optional[str] = Header(None, alias="x-resinkit-pat"), authorization: Optional[str] = Header(None)):
    # Check x-resinkit-pat header first, then fall back to authorization header
    pat = x_resinkit_pat or authorization

    if not pat:
        raise HTTPException(status_code=401, detail="Authorization failed")

    # Check cache first
    cached_result = _get_cached_result(pat)
    if cached_result is not None:
        logger.info("Returning cached result for PAT")
        return cached_result

    if not settings.IS_PRODUCTION and settings.X_RESINKIT_PAT:
        if pat != settings.X_RESINKIT_PAT:
            raise HTTPException(status_code=401, detail="Authorization failed")
        result = {"permissions": "*"}
        _cache_result(pat, result)
        return result

    # Call resink.ai to validate PAT
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://resink.ai/api/pat/validate", json={"token": pat}, headers={"accept": "application/json", "Content-Type": "application/json"}
            )
            logger.info(f"PAT validation response: {response.json()}")
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Authorization failed")

            result = response.json()
            if not result.get("valid", False):
                raise HTTPException(status_code=401, detail="Authorization failed")

            # Return the permissions from the API response
            permissions_result = {"permissions": result.get("permissions", [])}
            _cache_result(pat, permissions_result)
            return permissions_result

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error validating PAT: {str(e)}")
