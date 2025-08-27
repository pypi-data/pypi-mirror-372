import json

from resinkit_api.apps import get_mcp
from resinkit_api.core.logging import get_logger
from resinkit_api.db import data_sources_crud
from resinkit_api.db.database import get_db
from resinkit_api.services.agent.sql_tools import connection_manager

logger = get_logger(__name__)
mcp = get_mcp()


@mcp.resource(
    uri="resinkit://sources",
    name="Data Sources",
    description="List all available data sources (SQL databases, Kafka clusters, etc.)",
    mime_type="application/json",
)
async def list_data_sources() -> str:
    """List all data sources following REST API logic from data_sources_api.py"""
    db = None
    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)

        # Use async function directly
        sources = await data_sources_crud.list_data_sources(db)

        # Format response similar to REST API but without sensitive data
        sources_data = [
            {
                "name": source.name,
                "kind": source.kind,
                "host": source.host,
                "port": source.port,
                "database": source.database,
                "query_timeout": source.query_timeout,
                "extra_params": source.get_extra_params(),
                "created_at": source.created_at.isoformat(),
                "updated_at": source.updated_at.isoformat(),
                "created_by": source.created_by,
            }
            for source in sources
        ]

        return json.dumps({"sources": sources_data, "total_count": len(sources_data)}, indent=2)

    except Exception as e:
        logger.error(f"Failed to list SQL sources: {str(e)}", exc_info=True)
        return json.dumps({"error": f"Failed to list SQL sources: {str(e)}", "sources": [], "total_count": 0}, indent=2)
    finally:
        if db:
            db.close()


@mcp.resource(
    uri="resinkit://sources/{source_name}/tables", name="SQL Source Tables", description="List tables in a SQL data source", mime_type="application/json"
)
async def get_sql_source_tables(source_name: str) -> str:
    """Get tables for a SQL source following REST API logic from sql_tools_api.py:261"""
    db = None
    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)

        # Check if source exists (following REST API pattern)
        source = await data_sources_crud.get_data_source(db, source_name)
        if not source:
            return json.dumps({"error": f"SQL source with name '{source_name}' not found", "tables": [], "total_count": 0}, indent=2)

        # Get tables using connection manager
        tables = await connection_manager.list_tables(db, source_name)

        # Format response
        tables_data = [{"name": table.name, "schema_name": table.schema_name, "type": table.type} for table in tables]

        return json.dumps({"source_name": source_name, "tables": tables_data, "total_count": len(tables_data)}, indent=2)

    except Exception as e:
        logger.error(f"Failed to list tables for {source_name}: {str(e)}", exc_info=True)
        return json.dumps({"error": f"Failed to list tables for {source_name}: {str(e)}", "source_name": source_name, "tables": [], "total_count": 0}, indent=2)
    finally:
        if db:
            db.close()


@mcp.resource(
    uri="resinkit://sources/{source_name}/tables/{table_name}/schema",
    name="SQL Table Schema",
    description="Get schema/columns for a SQL table",
    mime_type="application/json",
)
async def get_sql_table_schema(source_name: str, table_name: str) -> str:
    """Get table schema following REST API logic from sql_tools_api.py:280"""
    db = None
    try:
        # Get database session
        db_gen = get_db()
        db = next(db_gen)

        # Check if source exists (following REST API pattern)
        source = await data_sources_crud.get_data_source(db, source_name)
        if not source:
            return json.dumps(
                {
                    "error": f"SQL source with name '{source_name}' not found",
                    "source_name": source_name,
                    "table_name": table_name,
                    "columns": [],
                    "total_columns": 0,
                },
                indent=2,
            )

        # Get table columns using connection manager
        # Note: schema_name is optional, could be passed as query parameter in future
        columns = await connection_manager.get_table_columns(db, source_name, table_name)

        # Format response
        columns_data = [{"name": col.name, "type": col.type, "nullable": col.nullable, "default": col.default, "comment": col.comment} for col in columns]

        return json.dumps({"source_name": source_name, "table_name": table_name, "columns": columns_data, "total_columns": len(columns_data)}, indent=2)

    except Exception as e:
        logger.error(f"Failed to get columns for {source_name}.{table_name}: {str(e)}", exc_info=True)
        return json.dumps(
            {
                "error": f"Failed to get columns for {source_name}.{table_name}: {str(e)}",
                "source_name": source_name,
                "table_name": table_name,
                "columns": [],
                "total_columns": 0,
            },
            indent=2,
        )
    finally:
        if db:
            db.close()
