from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Path, Query, UploadFile, status
from sqlalchemy.orm import Session

from resinkit_api.core.logging import get_logger
from resinkit_api.db.database import get_db
from resinkit_api.dependencies.data_sources import get_data_source_service
from resinkit_api.services.agent.data_sources_service import DataSourceService
from resinkit_api.services.agent.sql_tools import (
    ColumnInfo,
    DatabaseInfo,
    DataSourceConnectionTestResult,
    DataSourceCreate,
    DataSourceQueryRequest,
    DataSourceQueryResult,
    DataSourceResponse,
    DataSourceUpdate,
    SchemaInfo,
    TableInfo,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/agent/data-sources", tags=["data-sources", "mcp", "ai"])


@router.post(
    "/sources",
    status_code=status.HTTP_201_CREATED,
    response_model=DataSourceResponse,
    response_model_exclude_none=True,
    operation_id="create_data_source",
    summary="Create a new data source",
    description="Create a new data source configuration for database connections",
)
async def create_data_source(
    source: DataSourceCreate,
    db: Session = Depends(get_db),
    service: DataSourceService = Depends(get_data_source_service),
    created_by: str = "user",
) -> DataSourceResponse:
    """Create a new data source"""
    try:
        return await service.create_data_source(db, source, created_by)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create data source: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post(
    "/test-connection",
    response_model=DataSourceConnectionTestResult,
    operation_id="test_data_source_connection",
    summary="Test database connection",
    description="Test database connection without persisting credentials",
)
async def test_data_source_connection(
    source: DataSourceCreate,
    service: DataSourceService = Depends(get_data_source_service),
) -> DataSourceConnectionTestResult:
    """Test database connection without persisting credentials"""
    try:
        result = await service.test_connection(source)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test connection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/sources",
    response_model=List[DataSourceResponse],
    response_model_exclude_none=True,
    operation_id="list_data_sources",
    summary="List all data sources",
    description="Get a list of all configured data sources",
)
async def list_data_sources(
    db: Session = Depends(get_db),
    service: DataSourceService = Depends(get_data_source_service),
) -> List[DataSourceResponse]:
    """List all data sources"""
    try:
        return await service.list_data_sources(db)
    except Exception as e:
        logger.error(f"Failed to list data sources: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/sources/{source_name}",
    response_model=DataSourceResponse,
    response_model_exclude_none=True,
    operation_id="get_data_source",
    summary="Get data source by name",
    description="Retrieve a specific data source configuration by name",
)
async def get_data_source(
    source_name: str = Path(..., description="Name of the data source"),
    db: Session = Depends(get_db),
    service: DataSourceService = Depends(get_data_source_service),
) -> DataSourceResponse:
    """Get a data source by name"""
    try:
        result = await service.get_data_source(db, source_name)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data source with name '{source_name}' not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get data source: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.put(
    "/sources/{source_name}",
    response_model=DataSourceResponse,
    response_model_exclude_none=True,
    operation_id="update_data_source",
    summary="Update data source",
    description="Update an existing data source configuration",
)
async def update_data_source(
    source_name: str = Path(..., description="Name of the data source to update"),
    source_update: DataSourceUpdate = ...,
    db: Session = Depends(get_db),
    service: DataSourceService = Depends(get_data_source_service),
) -> DataSourceResponse:
    """Update a data source"""
    try:
        result = await service.update_data_source(db, source_name, source_update)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data source with name '{source_name}' not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update data source: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.delete(
    "/sources/{source_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="delete_data_source",
    summary="Delete data source",
    description="Delete a data source configuration",
)
async def delete_data_source(
    source_name: str = Path(..., description="Name of the data source to delete"),
    db: Session = Depends(get_db),
    service: DataSourceService = Depends(get_data_source_service),
) -> None:
    """Delete a data source"""
    try:
        success = await service.delete_data_source(db, source_name)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data source with name '{source_name}' not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete data source: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/sources/{source_name}/databases",
    response_model=List[DatabaseInfo],
    operation_id="list_sql_databases",
    summary="List databases",
    description="List databases available in a data source",
)
async def list_databases(
    source_name: str = Path(..., description="Name of the data source"),
    db: Session = Depends(get_db),
    service: DataSourceService = Depends(get_data_source_service),
) -> List[DatabaseInfo]:
    """List databases in a data source"""
    try:
        result = await service.list_databases(db, source_name)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data source with name '{source_name}' not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list databases for {source_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/sources/{source_name}/schemas",
    response_model=List[SchemaInfo],
    operation_id="list_sql_schemas",
    summary="List schemas",
    description="List schemas available in a database",
)
async def list_schemas(
    source_name: str = Path(..., description="Name of the data source"),
    database_name: Optional[str] = Query(None, description="Optional database name filter"),
    db: Session = Depends(get_db),
    service: DataSourceService = Depends(get_data_source_service),
) -> List[SchemaInfo]:
    """List schemas in a database"""
    try:
        result = await service.list_schemas(db, source_name, database_name)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data source with name '{source_name}' not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list schemas for {source_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/sources/{source_name}/tables",
    response_model=List[TableInfo],
    operation_id="list_sql_tables",
    summary="List tables",
    description="List tables available in a schema",
)
async def list_tables(
    source_name: str = Path(..., description="Name of the data source"),
    schema_name: Optional[str] = Query(None, description="Optional schema name filter"),
    db: Session = Depends(get_db),
    service: DataSourceService = Depends(get_data_source_service),
) -> List[TableInfo]:
    """List tables in a schema"""
    try:
        result = await service.list_tables(db, source_name, schema_name)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data source with name '{source_name}' not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list tables for {source_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/sources/{source_name}/tables/{table_name}/columns",
    response_model=List[ColumnInfo],
    operation_id="get_sql_table_columns",
    summary="Get table columns",
    description="Get column information for a specific table",
)
async def get_table_columns(
    source_name: str = Path(..., description="Name of the data source"),
    table_name: str = Path(..., description="Name of the table"),
    schema_name: Optional[str] = Query(None, description="Optional schema name"),
    db: Session = Depends(get_db),
    service: DataSourceService = Depends(get_data_source_service),
) -> List[ColumnInfo]:
    """Get columns for a table"""
    try:
        result = await service.get_table_columns(db, source_name, table_name, schema_name)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data source with name '{source_name}' not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get columns for {source_name}.{table_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post(
    "/query",
    response_model=DataSourceQueryResult,
    operation_id="execute_query",
    summary="Execute SQL query",
    description="Execute a SQL query against a data source",
)
async def execute_query(
    query_request: DataSourceQueryRequest,
    db: Session = Depends(get_db),
    service: DataSourceService = Depends(get_data_source_service),
) -> DataSourceQueryResult:
    """Execute a SQL query against a data source"""
    try:
        result = await service.execute_query(db, query_request)
        if result is None:
            if await service.get_data_source(db, query_request.source_name) is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Data source with name '{query_request.source_name}' not found")
            raise HTTPException(status_code=500, detail="Failed to execute query - connection error")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query execution failed: {str(e)}")


@router.get(
    "/sqlite-files",
    response_model=List[str],
    operation_id="list_sqlite_files",
    summary="List SQLite files",
    description="List all available SQLite database files",
)
async def list_sqlite_files(
    service: DataSourceService = Depends(get_data_source_service),
) -> List[str]:
    """List all SQLite files in the SQLITE_FOLDER"""
    try:
        return await service.list_sqlite_files()
    except Exception as e:
        logger.error(f"Failed to list SQLite files: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post(
    "/sqlite-files",
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
    operation_id="upload_sqlite_file",
    summary="Upload SQLite file",
    description="Upload a SQLite database file",
)
async def upload_sqlite_file(
    file: UploadFile = File(..., description="SQLite database file to upload"),
    service: DataSourceService = Depends(get_data_source_service),
) -> dict:
    """Upload a SQLite file to the SQLITE_FOLDER"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="File name is required")

        if not file.filename.endswith(".sqlite"):
            raise HTTPException(status_code=400, detail="Only .sqlite files are allowed")

        filename = await service.upload_sqlite_file(file)
        return {"filename": filename, "message": "File uploaded successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload SQLite file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
