import asyncio
import logging
from typing import Any, Dict

import httpx
from aiokafka import AIOKafkaProducer
from fastapi import APIRouter

router = APIRouter(tags=["health"])

logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check():
    return {"status": "OK"}


@router.get("/sysinfo")
async def system_info():
    """
    Check the health status of all ResinKit components
    """
    components = {
        "flink_job_manager": await check_flink_job_manager(),
        "flink_sql_gateway": await check_flink_sql_gateway(),
        "kafka": await check_kafka(),
        "jupyterlab": await check_jupyterlab(),
    }

    # Overall system status
    all_healthy = all(comp["status"] == "healthy" for comp in components.values())

    return {"system_status": "healthy" if all_healthy else "degraded", "timestamp": asyncio.get_event_loop().time(), "components": components}


async def check_flink_job_manager() -> Dict[str, Any]:
    """Check Flink Job Manager health at http://localhost:8081"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8081/overview")
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "endpoint": "http://localhost:8081",
                    "details": {
                        "taskmanagers": data.get("taskmanagers", 0),
                        "slots_total": data.get("slots-total", 0),
                        "slots_available": data.get("slots-available", 0),
                    },
                }
            else:
                return {"status": "unhealthy", "endpoint": "http://localhost:8081", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "unhealthy", "endpoint": "http://localhost:8081", "error": str(e)}


async def check_flink_sql_gateway() -> Dict[str, Any]:
    """Check Flink SQL Gateway health at http://localhost:8083"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8083/v1/info")
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "endpoint": "http://localhost:8083",
                    "details": {"product_name": data.get("productName", "unknown"), "version": data.get("version", "unknown")},
                }
            else:
                return {"status": "unhealthy", "endpoint": "http://localhost:8083", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "unhealthy", "endpoint": "http://localhost:8083", "error": str(e)}


async def check_kafka() -> Dict[str, Any]:
    """Check Kafka health at localhost:9092"""
    try:
        producer = AIOKafkaProducer(bootstrap_servers="localhost:9092", request_timeout_ms=5000, connections_max_idle_ms=5000)
        await producer.start()

        # Get cluster metadata to verify connection
        cluster = producer.client.cluster
        brokers = list(cluster.brokers())

        await producer.stop()

        return {
            "status": "healthy",
            "endpoint": "localhost:9092",
            "details": {"brokers_count": len(brokers), "broker_ids": [broker.nodeId for broker in brokers]},
        }
    except Exception as e:
        return {"status": "unhealthy", "endpoint": "localhost:9092", "error": str(e)}


async def check_jupyterlab() -> Dict[str, Any]:
    """Check JupyterLab health at http://localhost:8888"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8888/api/status")
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "healthy",
                    "endpoint": "http://localhost:8888",
                    "details": {
                        "started": data.get("started"),
                        "last_activity": data.get("last_activity"),
                        "kernels": data.get("kernels", 0),
                        "connections": data.get("connections", 0),
                    },
                }
            else:
                return {"status": "unhealthy", "endpoint": "http://localhost:8888", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "unhealthy", "endpoint": "http://localhost:8888", "error": str(e)}


# Add other existing endpoints here if any
