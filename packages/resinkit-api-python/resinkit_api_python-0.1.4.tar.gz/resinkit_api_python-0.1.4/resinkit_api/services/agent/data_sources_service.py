import shutil
from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from resinkit_api.core.config import settings
from resinkit_api.core.logging import get_logger
from resinkit_api.db import data_sources_crud
from resinkit_api.db.models import DataSource
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
    connection_manager,
)

logger = get_logger(__name__)


class DataSourceService:
    """Service for managing data sources - handles business logic and data transformations"""

    async def create_data_source(
        self,
        db: Session,
        source_data: DataSourceCreate,
        created_by: str = "user",
    ) -> DataSourceResponse:
        """Create a new data source"""
        # Check if source already exists
        existing = await data_sources_crud.get_data_source(db, source_data.name)
        if existing:
            raise ValueError(f"Data source with name '{source_data.name}' already exists")

        # Create new source
        result = await data_sources_crud.create_data_source(
            db=db,
            name=source_data.name,
            kind=source_data.kind.value,
            host=source_data.host,
            port=source_data.port,
            database=source_data.database,
            user=source_data.user,
            password=source_data.password,
            query_timeout=source_data.query_timeout,
            extra_params=source_data.extra_params,
            created_by=created_by,
        )

        return self._build_response(result)

    async def list_data_sources(self, db: Session) -> List[DataSourceResponse]:
        """List all data sources"""
        sources = await data_sources_crud.list_data_sources(db)
        return [self._build_response(source) for source in sources]

    async def get_data_source(self, db: Session, source_name: str) -> Optional[DataSourceResponse]:
        """Get a data source by name"""
        source = await data_sources_crud.get_data_source(db, source_name)
        if not source:
            return None
        return self._build_response(source)

    async def update_data_source(
        self,
        db: Session,
        source_name: str,
        source_update: DataSourceUpdate,
    ) -> Optional[DataSourceResponse]:
        """Update a data source"""
        # Check if source exists
        existing = await data_sources_crud.get_data_source(db, source_name)
        if not existing:
            return None

        # Update source
        result = await data_sources_crud.update_data_source(
            db=db,
            name=source_name,
            host=source_update.host,
            port=source_update.port,
            database=source_update.database,
            user=source_update.user,
            password=source_update.password,
            query_timeout=source_update.query_timeout,
            extra_params=source_update.extra_params,
        )

        return self._build_response(result) if result else None

    async def delete_data_source(self, db: Session, source_name: str) -> bool:
        """Delete a data source"""
        # Check if source exists
        existing = await data_sources_crud.get_data_source(db, source_name)
        if not existing:
            return False

        # Close any existing engine for this source
        connection_manager.close_engine(source_name)

        # Delete source
        return await data_sources_crud.delete_data_source(db, source_name)

    async def test_connection(self, source_data: DataSourceCreate) -> DataSourceConnectionTestResult:
        """Test database connection without persisting credentials"""
        result = await connection_manager.test_connection(
            kind=source_data.kind,
            host=source_data.host,
            port=source_data.port,
            database=source_data.database,
            user=source_data.user,
            password=source_data.password,
            extra_params=source_data.extra_params,
        )
        return result

    async def list_databases(self, db: Session, source_name: str) -> Optional[List[DatabaseInfo]]:
        """List databases in a data source"""
        # Check if source exists
        source = await data_sources_crud.get_data_source(db, source_name)
        if not source:
            return None

        databases = await connection_manager.list_databases(db, source_name)
        return databases

    async def list_schemas(self, db: Session, source_name: str, database_name: Optional[str] = None) -> Optional[List[SchemaInfo]]:
        """List schemas in a database"""
        # Check if source exists
        source = await data_sources_crud.get_data_source(db, source_name)
        if not source:
            return None

        schemas = await connection_manager.list_schemas(db, source_name, database_name)
        return schemas

    async def list_tables(self, db: Session, source_name: str, schema_name: Optional[str] = None) -> Optional[List[TableInfo]]:
        """List tables in a schema"""
        # Check if source exists
        source = await data_sources_crud.get_data_source(db, source_name)
        if not source:
            return None

        tables = await connection_manager.list_tables(db, source_name, schema_name)
        return tables

    async def get_table_columns(
        self,
        db: Session,
        source_name: str,
        table_name: str,
        schema_name: Optional[str] = None,
    ) -> Optional[List[ColumnInfo]]:
        """Get columns for a table"""
        # Check if source exists
        source = await data_sources_crud.get_data_source(db, source_name)
        if not source:
            return None

        columns = await connection_manager.get_table_columns(db, source_name, table_name, schema_name)
        return columns

    async def execute_query(self, db: Session, query_request: DataSourceQueryRequest) -> Optional[DataSourceQueryResult]:
        """Execute a SQL query against a data source"""
        # Check if source exists
        logger.info(f"Executing query: {query_request.query}")
        source = await data_sources_crud.get_data_source(db, query_request.source_name)
        if not source:
            return None

        # Execute query
        result = await connection_manager.execute_query(db, query_request.source_name, query_request.query)
        return result

    def _build_response(self, data_source: DataSource) -> DataSourceResponse:
        """Build a DataSourceResponse from a DataSource model, excluding null fields"""
        response_data = {
            "name": data_source.name,
            "kind": data_source.kind,
            "database": data_source.database,
            "query_timeout": data_source.query_timeout,
            "extra_params": data_source.get_extra_params(),
            "created_at": data_source.created_at.isoformat(),
            "updated_at": data_source.updated_at.isoformat(),
            "created_by": data_source.created_by,
        }

        # Only include host, port, user if they're not null
        if data_source.host is not None:
            response_data["host"] = data_source.host
        if data_source.port is not None:
            response_data["port"] = data_source.port
        if data_source.encrypted_user is not None:
            response_data["user"] = "***"  # Don't expose actual user in response

        return DataSourceResponse(**response_data)

    async def list_sqlite_files(self) -> List[str]:
        """List all SQLite files in the SQLITE_FOLDER"""
        sqlite_folder = settings.SQLITE_FOLDER_PATH
        sqlite_files = []

        try:
            # List all .sqlite files in the folder
            for file_path in sqlite_folder.glob("*.sqlite"):
                if file_path.is_file():
                    sqlite_files.append(file_path.name)

            return sorted(sqlite_files)
        except Exception as e:
            logger.error(f"Failed to list SQLite files: {str(e)}")
            raise

    async def upload_sqlite_file(self, file: UploadFile) -> str:
        """Upload a SQLite file to the SQLITE_FOLDER"""
        sqlite_folder = settings.SQLITE_FOLDER_PATH

        try:
            # Ensure the filename ends with .sqlite
            filename = file.filename
            if not filename or not filename.endswith(".sqlite"):
                raise ValueError("Only .sqlite files are allowed")

            # Create the file path
            file_path = sqlite_folder / filename

            # Write the uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            logger.info(f"Successfully uploaded SQLite file: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Failed to upload SQLite file: {str(e)}")
            raise
