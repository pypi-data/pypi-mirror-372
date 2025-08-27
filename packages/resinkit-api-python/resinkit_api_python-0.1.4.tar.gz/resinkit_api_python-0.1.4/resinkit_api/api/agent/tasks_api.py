from typing import Dict, List, Optional

import yaml
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from resinkit_api.core.logging import get_logger
from resinkit_api.db import variables_crud
from resinkit_api.db.database import get_db
from resinkit_api.services.agent import get_active_task_manager
from resinkit_api.services.agent.data_models import InvalidTaskError, TaskConflictError, TaskNotFoundError, TaskResult, UnprocessableTaskError
from resinkit_api.services.agent.task_runner_base import LogEntry
from resinkit_api.services.agent.task_tiq_manager import TaskTiqManager

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/agent", tags=["tasks", "mcp", "ai"])


# 1. Submit a new Task with variable resolution
@router.post("/tasks", status_code=status.HTTP_202_ACCEPTED, operation_id="submit_resinkit_task")
async def submit_task(payload: dict = Body(...), task_manager: TaskTiqManager = Depends(get_active_task_manager), db: Session = Depends(get_db)):
    try:
        # Process payload for variable substitution if it contains string fields
        processed_payload = await process_payload_variables(payload, db)

        # Submit the processed task
        result = await task_manager.submit_task(processed_payload, db)
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=result)
    except InvalidTaskError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnprocessableTaskError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# Process payload variables recursively
async def process_payload_variables(payload: Dict, db: Session) -> Dict:
    """
    Process payload to replace variable references with their values.
    Handles nested dictionaries and lists.
    """
    if isinstance(payload, dict):
        return {k: await process_payload_variables(v, db) for k, v in payload.items()}
    elif isinstance(payload, list):
        return [await process_payload_variables(item, db) for item in payload]
    elif isinstance(payload, str):
        # Replace variables in strings
        return await variables_crud.resolve_variables(db, payload)
    else:
        # Return other types as is
        return payload


# New endpoint for YAML task submission with variable resolution
@router.post("/tasks/yaml", status_code=status.HTTP_202_ACCEPTED, operation_id="submit_resinkit_task_yaml")
async def submit_task_yaml(
    yaml_payload: str = Body(...),
    task_manager: TaskTiqManager = Depends(get_active_task_manager),
    db: Session = Depends(get_db),
):
    try:
        # Process YAML string for variable substitution
        processed_yaml = await variables_crud.resolve_variables(db, yaml_payload)

        # Convert YAML to dictionary
        payload = yaml.safe_load(processed_yaml)
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="Invalid YAML: must represent a dictionary")

        # Submit the processed task
        result = await task_manager.submit_task(payload, db)
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=result)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML format: {str(e)}")
    except InvalidTaskError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnprocessableTaskError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to submit task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# 2. Get Task Details
@router.get("/tasks/{task_id}", operation_id="get_resinkit_task_details")
async def get_task_details(
    task_id: str = Path(...),
    task_manager: TaskTiqManager = Depends(get_active_task_manager),
    db: Session = Depends(get_db),
):
    try:
        return await task_manager.get_task_details(task_id, db)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# 3. List Tasks
@router.get("/tasks", operation_id="list_resinkit_tasks")
async def list_tasks(
    task_type: Optional[str] = Query(None),
    status_: Optional[str] = Query(None, alias="status"),
    task_name_contains: Optional[str] = Query(None),
    tags_include_any: Optional[str] = Query(None),
    created_after: Optional[str] = Query(None),
    created_before: Optional[str] = Query(None),
    limit: Optional[int] = Query(20, ge=1, le=100),
    page_token: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("created_at"),
    sort_order: Optional[str] = Query("desc"),
    task_manager: TaskTiqManager = Depends(get_active_task_manager),
    db: Session = Depends(get_db),
):
    try:
        return await task_manager.list_tasks(
            db, task_type, status_, task_name_contains, tags_include_any, created_after, created_before, limit, page_token, sort_by, sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# 4. Cancel a Task
@router.post("/tasks/{task_id}/cancel", status_code=status.HTTP_202_ACCEPTED, operation_id="cancel_resinkit_task")
async def cancel_task(
    task_id: str = Path(...),
    force: bool = Query(False, description="Whether to forcefully cancel the task"),
    task_manager: TaskTiqManager = Depends(get_active_task_manager),
    db: Session = Depends(get_db),
):
    try:
        result = await task_manager.cancel_task(task_id, db, force=force)
        return JSONResponse(content=result)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    except TaskConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except UnprocessableTaskError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# 5. Get Task Logs
@router.get("/tasks/{task_id}/logs", response_model=List[LogEntry], operation_id="get_resinkit_task_logs")
async def get_task_logs(
    task_id: str = Path(...),
    level: str = Query("INFO", description="Log level filter (INFO, WARN, ERROR, DEBUG)"),
    task_manager: TaskTiqManager = Depends(get_active_task_manager),
    db: Session = Depends(get_db),
):
    try:
        return await task_manager.get_task_logs(task_id, db, log_level_filter=level)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# 6. Get Task Results
@router.get("/tasks/{task_id}/results", response_model=TaskResult, operation_id="get_resinkit_task_results")
async def get_task_results(task_id: str = Path(...), task_manager: TaskTiqManager = Depends(get_active_task_manager), db: Session = Depends(get_db)):
    try:
        return await task_manager.get_task_results(task_id, db)
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


# New endpoint: Permanently delete a task and its events if in end state
@router.delete("/tasks/{task_id}/permanent", status_code=status.HTTP_200_OK, operation_id="delete_resinkit_task_permanent")
async def permanently_delete_task(
    task_id: str = Path(...),
    db: Session = Depends(get_db),
    task_manager: TaskTiqManager = Depends(get_active_task_manager),
):
    """Permanently delete a task and its events if the task is in an end state (COMPLETED, FAILED, CANCELLED, or expired)."""
    try:
        await task_manager.permanently_delete_task(task_id, db)
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Task permanently deleted"})
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
    except TaskConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
