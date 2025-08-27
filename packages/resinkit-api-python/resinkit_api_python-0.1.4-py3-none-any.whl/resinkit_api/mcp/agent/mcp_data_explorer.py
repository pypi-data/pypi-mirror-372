"""
MCP tools for data exploration and discovery

This module provides MCP tools for exploring data sources and schemas,
following the design principles for clear, action-oriented naming and
strongly-typed schemas.
"""

from typing import Any, List, Optional, Union

from fastmcp import Context
from pydantic import BaseModel, Field, field_validator

from resinkit_api.apps import get_mcp
from resinkit_api.core.logging import get_logger
from resinkit_api.db.database import get_db
from resinkit_api.services.agent.data_explorer_service import DataExplorerService
from resinkit_api.services.flink_session_service import FlinkSessionService

logger = get_logger(__name__)
mcp = get_mcp()

# Create a singleton instance of FlinkSessionService for MCP tools
_flink_session_service_instance: Optional[FlinkSessionService] = None
_data_explorer_service_instance: Optional[DataExplorerService] = None


def get_flink_session_service() -> FlinkSessionService:
    """Get Flink session service singleton for MCP tools."""
    global _flink_session_service_instance
    if _flink_session_service_instance is None:
        _flink_session_service_instance = FlinkSessionService()
    return _flink_session_service_instance


def get_data_explorer_service() -> DataExplorerService:
    global _data_explorer_service_instance
    if _data_explorer_service_instance is None:
        _data_explorer_service_instance = DataExplorerService(get_flink_session_service())
    return _data_explorer_service_instance


class ListDataSourcesResponse(BaseModel):
    """Response model for list_data_sources MCP tool"""

    sources: List[dict] = Field(..., description="List of registered data sources")
    total_count: int = Field(..., description="Total number of data sources")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class GetDataSourceSchemasRequest(BaseModel):
    """Request model for get_data_source_schemas MCP tool"""

    source: str = Field(..., description="Data source name (SQL database, Kafka cluster, or other data source configured via /sources endpoints)")
    sample_count: int = Field(3, description="Number of sample rows/messages to retrieve for schema analysis from each table/topic")


class GetDataSourceSchemasResponse(BaseModel):
    """Response model for get_data_source_schemas MCP tool"""

    source: str = Field(..., description="Data source name")
    schemas: List[str] = Field(..., description="List of DSDS (Descriptive Sample Data Schema) strings for each data entity (table/topic/collection)")
    total_entities: int = Field(..., description="Total number of data entities found (tables/topics/collections)")
    source_type: str = Field(..., description="Type of data source (sql, kafka, etc.)")
    error: Optional[str] = Field(None, description="Error message if operation failed")


class ExecuteSqlQueryRequest(BaseModel):
    """Request model for execute_sql_query MCP tool"""

    source: Optional[str] = Field(None, description="Optional data source name. If not specified or if the source is of Kafka kind, uses Flink SQL engine")
    query: str = Field(..., description="SQL query to execute")
    limit: Optional[Union[str, int]] = Field(1000, description="Maximum number of rows to return (default: 1000)")

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v):
        """Convert string limit to integer and validate range"""
        if v is None:
            return 1000  # Default value

        if isinstance(v, str):
            try:
                v = int(v)
            except ValueError:
                raise ValueError(f"limit must be a valid integer, got: {v}")

        if isinstance(v, int):
            if v < 0:
                raise ValueError("limit must be non-negative")
            if v > 100000:  # Reasonable upper bound to prevent memory issues
                raise ValueError("limit cannot exceed 100,000 rows")
            return v

        raise ValueError(f"limit must be an integer or string, got: {type(v)}")


class ExecuteSqlQueryResponse(BaseModel):
    """Response model for execute_sql_query MCP tool"""

    source: str = Field(..., description="Data source name used for execution (or 'flink_default' if none specified)")
    query: str = Field(..., description="The SQL query that was executed")
    columns: List[str] = Field(default_factory=list, description="List of column names in the result set")
    rows: List[List[Any]] = Field(default_factory=list, description="List of result rows, each row as a list of values")
    row_count: int = Field(0, description="Total number of rows returned")
    execution_time_ms: float = Field(0.0, description="Query execution time in milliseconds")
    error: Optional[str] = Field(None, description="Detailed error message if operation failed")
    error_type: Optional[str] = Field(None, description="Type of error (syntax, connection, permission, etc.)")
    troubleshooting_tips: Optional[str] = Field(None, description="Helpful tips for resolving the error")


@mcp.tool
async def list_data_sources() -> ListDataSourcesResponse:
    """
    List all registered data sources available for querying.

    This tool returns a list of all data sources (SQL databases, Kafka clusters, etc.)
    that have been configured and are available for crawling and exploration. Use this
    tool to discover what data sources are available before exploring their schemas.

    Returns:
        ListDataSourcesResponse with list of data sources and their metadata
    """
    db = None
    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)

        # Use service layer for business logic
        service = get_data_explorer_service()
        sources_data = await service.list_data_sources(db)

        return ListDataSourcesResponse(sources=sources_data, total_count=len(sources_data))

    except Exception as e:
        logger.error(f"Failed to list data sources: {str(e)}", exc_info=True)
        return ListDataSourcesResponse(sources=[], total_count=0, error=f"Failed to list data sources: {str(e)}")
    finally:
        if db:
            db.close()


@mcp.tool
async def get_data_source_schemas(
    source: str = Field(..., description="Data source name (SQL database, Kafka cluster, or other data source configured via /sources endpoints)"),
    sample_count: int = Field(3, description="Number of sample rows/messages to retrieve for schema analysis from each table/topic"),
) -> GetDataSourceSchemasResponse:
    """
    Retrieve data definition and sample data for all data entities in a specified data source.

    This tool supports multiple data source types including SQL databases, Kafka clusters,
    and other data systems. It analyzes sample data to generate DSDS (Descriptive Sample
    Data Schema) strings that describe the structure, types, and characteristics of data.

    For SQL databases: Crawls all tables and generates schema descriptions with sample data.
    For Kafka clusters: Crawls all topics (excluding internal topics) and analyzes message schemas.
    For other sources: Adapts to the specific data model of the source type.

    Args:
        source: Data source name (SQL database, Kafka cluster, or other data source configured via /sources endpoints)
        sample_count: Number of sample rows/messages to retrieve for schema analysis from each table/topic

    Returns:
        GetDataSourceSchemasResponse with DSDS strings for all data entities
    """
    db = None
    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)

        # Use service layer for business logic
        service = get_data_explorer_service()
        result = await service.get_data_source_schemas(db, source, sample_count)

        return GetDataSourceSchemasResponse(
            source=source,
            schemas=result["schemas"],
            total_entities=result["total_entities"],
            source_type=result["source_type"],
            error=result.get("error"),
        )

    except Exception as e:
        logger.error(f"Failed to get schemas for {source}: {str(e)}", exc_info=True)
        return GetDataSourceSchemasResponse(source=source, schemas=[], total_entities=0, source_type="unknown", error=f"Failed to get schemas: {str(e)}")
    finally:
        if db:
            db.close()


@mcp.tool
async def get_sql_schema_with_query(
    ctx: Context,
    source: str = Field(..., description="SQL-compatible data source name (configured via /sources endpoints)"),
    query: str = Field(..., description="SQL query to execute for schema generation"),
    table_name: str = Field("query_result", description="Name to use for the resulting schema"),
) -> GetDataSourceSchemasResponse:
    """
    Retrieve data definition and sample data in a specified data source using a custom SQL query.

    This tool executes a custom SQL query and generates a DSDS (Descriptive Sample Data Schema)
    for the result set. This is useful for understanding the structure and sample data
    of complex queries, joins, or specific column selections. The query should be a SELECT
    statement that returns the columns you want to analyze.

    For SQL-compatible data sources (MySQL, PostgreSQL, Oracle, MSSQL,SQLite, StarRocks). It will directly
    execute the query on the data source. For kafka it will use Flink as the engine to execute the query.
    If no engine is available, it will return an error.

    Args:
        ctx: FastMCP context for progress reporting and cancellation detection
        source: SQL-compatible data source name (configured via /sources endpoints)
        query: SQL query to execute for schema generation
        table_name: Name to use for the resulting schema

    Returns:
        GetDataSourceSchemasResponse with DSDS string for the query result
    """
    db = None
    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)

        # Use service layer for business logic
        service = get_data_explorer_service()
        result = await service.get_sql_schema_with_query(db, source, query, table_name, ctx)

        # Convert single schema to list format to match GetDataSourceSchemasResponse
        schema = result.get("schema", "")
        schemas = [schema] if schema else []

        return GetDataSourceSchemasResponse(
            source=source,
            schemas=schemas,
            total_entities=1 if schema else 0,
            source_type="sql",  # This is a SQL query
            error=result.get("error"),
        )

    except Exception as e:
        logger.error(f"Failed to get schema with query for {source}: {str(e)}", exc_info=True)
        return GetDataSourceSchemasResponse(source=source, schemas=[], total_entities=0, source_type="sql", error=f"Failed to get schema with query: {str(e)}")
    finally:
        if db:
            db.close()


@mcp.tool
async def execute_sql_query(
    ctx: Context,
    query: str = Field(..., description="SQL query to execute"),
    source: Optional[str] = Field(None, description="Optional data source name. If not specified or if the source is of Kafka kind, uses Flink SQL engine"),
) -> ExecuteSqlQueryResponse:
    """
    Execute a SQL query using the appropriate engine based on the data source type.

    This tool executes SQL queries with comprehensive error handling and provides
    detailed troubleshooting information when queries fail. Use this tool when you
    need to run custom SQL queries and want detailed feedback about execution results
    or errors. The tool supports all standard SQL operations (SELECT, INSERT, UPDATE, DELETE)
    and provides semantic error messages to help diagnose and fix query issues.

    Engine Selection Logic:
    - If no source is specified: Uses Flink SQL engine
    - If source is of Kafka kind: Uses Flink SQL engine
    - For SQL-compatible data sources (MySQL, PostgreSQL, Oracle, MSSQL, SQLite, StarRocks):
      Executes directly on the data source
    - If source not found: Falls back to Flink SQL engine

    Users are responsible for controlling result limits by including LIMIT clauses in their queries.

    Args:
        ctx: FastMCP context for progress reporting and cancellation detection
        query: SQL query to execute
        source: Optional data source name. If not specified or if the source is of Kafka kind, uses Flink SQL engine

    Returns:
        ExecuteSqlQueryResponse with query results or detailed error information
    """
    db = None
    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)

        # Use service layer for business logic
        service = get_data_explorer_service()
        result = await service.execute_sql_query_with_validation(db, source, query, ctx)

        return ExecuteSqlQueryResponse(
            source=source or "flink_default",
            query=query,
            columns=result.get("columns", []),
            rows=result.get("rows", []),
            row_count=result.get("row_count", 0),
            execution_time_ms=result.get("execution_time_ms", 0.0),
            error=result.get("error"),
            error_type=result.get("error_type"),
            troubleshooting_tips=result.get("troubleshooting_tips"),
        )

    except Exception as e:
        logger.error(f"Failed to execute SQL query for {source or 'flink_default'}: {str(e)}", exc_info=True)
        return ExecuteSqlQueryResponse(
            source=source or "flink_default",
            query=query,
            columns=[],
            rows=[],
            row_count=0,
            execution_time_ms=0.0,
            error=f"Failed to execute SQL query: {str(e)}",
            error_type="internal_error",
            troubleshooting_tips="An internal error occurred. Check the logs for more details.",
        )
    finally:
        if db:
            db.close()
