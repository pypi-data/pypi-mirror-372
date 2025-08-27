from fastapi import APIRouter, HTTPException, status

from resinkit_api.core.logging import get_logger
from resinkit_api.services.agent.kafka_crawl.models import KafkaCrawlRequest, KafkaCrawlResult
from resinkit_api.services.agent.kafka_crawl.service import KafkaCrawlService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/agent/kafka-crawl", tags=["kafka-crawl", "mcp", "ai"])


@router.post(
    "/crawl",
    status_code=status.HTTP_200_OK,
    response_model=KafkaCrawlResult,
    summary="Crawl Kafka topics",
    description="Crawl specified Kafka topics and return structured knowledge including schemas, sample messages, and field analysis",
    operation_id="crawl_kafka_topics",
)
async def crawl_kafka_topics(request: KafkaCrawlRequest) -> KafkaCrawlResult:
    """
    Crawl Kafka topics according to the provided configuration.

    This endpoint performs the following operations:
    1. Validates the crawl configuration
    2. Connects to the specified Kafka cluster
    3. Discovers and crawls the configured topics
    4. Consumes sample messages from each topic
    5. Infers JSON schemas from message structures
    6. Generates field-level analysis and statistics
    7. Returns structured JSON result
    """
    try:
        # Initialize service
        service = KafkaCrawlService()

        # Execute crawl
        result = await service.execute_crawl(request.config)

        return result

    except ValueError as e:
        # Configuration validation errors
        logger.error(f"Configuration validation error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Configuration validation failed: {str(e)}")

    except Exception as e:
        # General execution errors
        logger.error(f"Kafka crawl failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Kafka crawl operation failed: {str(e)}")
