"""
TaskIQ Broker Configuration

This module provides TaskIQ broker and result backend configuration.
"""

import os
from typing import Optional

from taskiq import AsyncBroker, InMemoryBroker
from taskiq.abc import AsyncResultBackend
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from resinkit_api.core.logging import get_logger

logger = get_logger(__name__)


# Global instances
_broker: Optional[InMemoryBroker] = None
_result_backend: Optional[AsyncResultBackend] = None


def get_taskiq_broker() -> AsyncBroker:
    """
    Get the TaskIQ broker instance.

    Returns:
        TaskIQ broker instance (Redis or InMemory for testing)
    """
    global _broker

    if _broker is None:
        redis_url = os.getenv("REDIS_URL")

        if redis_url:
            logger.info("Initializing Redis TaskIQ broker with URL: %s", redis_url)
            try:
                _broker = ListQueueBroker(url=redis_url)
            except Exception as e:
                logger.warning("Failed to initialize Redis broker, falling back to InMemory: %s", str(e))
                _broker = InMemoryBroker()
        else:
            logger.info("No Redis URL provided, using InMemory TaskIQ broker")
            _broker = InMemoryBroker()

    return _broker


def get_taskiq_result_backend() -> AsyncResultBackend:
    """
    Get the TaskIQ result backend instance.

    Returns:
        TaskIQ result backend instance (Redis or InMemory for testing)
    """
    global _result_backend

    if _result_backend is None:
        redis_url = os.getenv("REDIS_URL")

        if redis_url:
            logger.info("Initializing Redis TaskIQ result backend with URL: %s", redis_url)
            try:
                _result_backend = RedisAsyncResultBackend(url=redis_url)
            except Exception as e:
                logger.warning("Failed to initialize Redis result backend, using broker's default: %s", str(e))
                # For InMemory broker, use its default result backend
                broker = get_taskiq_broker()
                _result_backend = broker.result_backend
        else:
            logger.info("No Redis URL provided, using broker's default result backend")
            # For InMemory broker, use its default result backend
            broker = get_taskiq_broker()
            _result_backend = broker.result_backend

    return _result_backend


async def shutdown_taskiq():
    """Clean shutdown of TaskIQ components."""
    global _broker, _result_backend

    if _broker:
        logger.info("Shutting down TaskIQ broker")
        try:
            await _broker.shutdown()
        except Exception as e:
            logger.error("Error shutting down broker: %s", str(e))

    if _result_backend and hasattr(_result_backend, "shutdown"):
        logger.info("Shutting down TaskIQ result backend")
        try:
            await _result_backend.shutdown()
        except Exception as e:
            logger.error("Error shutting down result backend: %s", str(e))

    _broker = None
    _result_backend = None
