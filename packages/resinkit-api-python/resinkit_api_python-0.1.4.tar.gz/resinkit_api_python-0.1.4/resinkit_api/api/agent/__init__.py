from fastapi import APIRouter

from .data_sources_api import router as data_sources_router
from .db_crawl_api import router as db_crawl_router
from .kafka_crawl_api import router as kafka_crawl_router
from .tasks_api import router as tasks_router
from .variables_api import router as variables_router

# Create main agent router
router = APIRouter()

# Include sub-routers
router.include_router(tasks_router)
router.include_router(variables_router)
router.include_router(data_sources_router)
router.include_router(db_crawl_router)
router.include_router(kafka_crawl_router)
