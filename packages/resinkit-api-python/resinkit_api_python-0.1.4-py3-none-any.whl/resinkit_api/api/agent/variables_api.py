from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from resinkit_api.core.logging import get_logger
from resinkit_api.db import variables_crud
from resinkit_api.db.database import get_db

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/agent", tags=["variables", "mcp", "ai"])


# Variable models
class VariableCreate(BaseModel):
    name: str
    value: str
    description: Optional[str] = None


class VariableResponse(BaseModel):
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str
    created_by: str


class VariableUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None


# Variable API endpoints
@router.post(
    "/variables",
    status_code=status.HTTP_201_CREATED,
    response_model=VariableResponse,
    summary="Create a new variable",
    description="Create a new variable with encrypted value storage",
    operation_id="create_variable",
)
async def create_variable(
    variable: VariableCreate,
    db: Session = Depends(get_db),
    created_by: str = "user",  # In a real app, get this from auth
):
    """Create a new variable with encrypted value"""
    try:
        # Check if variable already exists
        existing = await variables_crud.get_variable(db, variable.name)
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Variable with name '{variable.name}' already exists")

        # Create new variable
        result = await variables_crud.create_variable(db=db, name=variable.name, value=variable.value, description=variable.description, created_by=created_by)

        # Return response without the encrypted value
        return VariableResponse(
            name=result.name,
            description=result.description,
            created_at=result.created_at.isoformat(),
            updated_at=result.updated_at.isoformat(),
            created_by=result.created_by,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create variable: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/variables",
    response_model=List[VariableResponse],
    summary="List all variables",
    description="List all variables without their encrypted values",
    operation_id="list_variables",
)
async def list_variables(db: Session = Depends(get_db)):
    """List all variables (without their values)"""
    try:
        variables = await variables_crud.list_variables(db)

        # Convert to response model
        return [
            VariableResponse(
                name=var.name,
                description=var.description,
                created_at=var.created_at.isoformat(),
                updated_at=var.updated_at.isoformat(),
                created_by=var.created_by,
            )
            for var in variables
        ]
    except Exception as e:
        logger.error(f"Failed to list variables: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/variables/{name}",
    response_model=VariableResponse,
    summary="Get a variable by name",
    description="Get a variable by name without its encrypted value",
    operation_id="get_variable",
)
async def get_variable(name: str, db: Session = Depends(get_db)):
    """Get a variable by name (without its value)"""
    try:
        variable = await variables_crud.get_variable(db, name)
        if not variable:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Variable with name '{name}' not found")

        # Return response without the encrypted value
        return VariableResponse(
            name=variable.name,
            description=variable.description,
            created_at=variable.created_at.isoformat(),
            updated_at=variable.updated_at.isoformat(),
            created_by=variable.created_by,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get variable: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.put(
    "/variables/{name}",
    response_model=VariableResponse,
    summary="Update a variable",
    description="Update a variable's value and/or description",
    operation_id="update_variable",
)
async def update_variable(name: str, variable_update: VariableUpdate, db: Session = Depends(get_db)):
    """Update a variable by name"""
    try:
        # Check if variable exists
        existing = await variables_crud.get_variable(db, name)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Variable with name '{name}' not found")

        # Update variable
        result = await variables_crud.update_variable(db=db, name=name, value=variable_update.value, description=variable_update.description)

        # Return response without the encrypted value
        return VariableResponse(
            name=result.name,
            description=result.description,
            created_at=result.created_at.isoformat(),
            updated_at=result.updated_at.isoformat(),
            created_by=result.created_by,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update variable: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.delete(
    "/variables/{name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a variable",
    description="Delete a variable by name",
    operation_id="delete_variable",
)
async def delete_variable(name: str, db: Session = Depends(get_db)):
    """Delete a variable by name"""
    try:
        # Check if variable exists
        existing = await variables_crud.get_variable(db, name)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Variable with name '{name}' not found")

        # Delete variable
        await variables_crud.delete_variable(db, name)

        # Return 204 No Content with no response body
        return
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete variable: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
