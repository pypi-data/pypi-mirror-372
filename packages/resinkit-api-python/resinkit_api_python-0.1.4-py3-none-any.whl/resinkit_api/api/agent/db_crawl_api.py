from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from resinkit_api.core.logging import get_logger
from resinkit_api.db.database import get_db
from resinkit_api.services.agent.db_crawl.models import DbCrawlRequest, DbCrawlResult
from resinkit_api.services.agent.db_crawl.service import DatabaseCrawlService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/agent/db-crawl", tags=["db-crawl", "mcp", "ai"])


@router.post(
    "/crawl",
    status_code=status.HTTP_200_OK,
    response_model=DbCrawlResult,
    summary="Crawl database tables",
    description="Crawl specified database tables and return structured knowledge including schema, sample data, and DSDS",
    operation_id="crawl_database_tables",
)
async def crawl_database(
    request: DbCrawlRequest,
    db: Session = Depends(get_db),
) -> DbCrawlResult:
    """
    Crawl database tables according to the provided configuration.

    This endpoint performs the following operations:
    1. Validates the crawl configuration
    2. Connects to the specified SQL source
    3. Crawls the configured tables
    4. Retrieves DDL and sample data
    5. Generates Descriptive Sample Data Schema (DSDS)
    6. Returns structured JSON result
    """
    try:
        # Initialize service
        service = DatabaseCrawlService()

        # Execute crawl
        result = await service.execute_crawl(db, request.config, request.save_remote)

        return result

    except ValueError as e:
        # Configuration validation errors
        logger.error(f"Configuration validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Configuration validation failed: {str(e)}")

    except Exception as e:
        # General execution errors
        logger.error(f"Database crawl failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database crawl operation failed: {str(e)}")
