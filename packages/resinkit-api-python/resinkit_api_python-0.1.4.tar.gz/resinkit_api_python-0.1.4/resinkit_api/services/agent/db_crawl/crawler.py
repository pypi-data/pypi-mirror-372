from typing import Any, Dict, List, Optional, Union

from sqlalchemy import text
from sqlalchemy.orm import Session

from resinkit_api.core.logging import get_logger
from resinkit_api.services.agent.db_crawl.config_parser import ConfigParser
from resinkit_api.services.agent.db_crawl.models import (
    TableRegexSelection,
    TableSelection,
)
from resinkit_api.services.agent.sql_tools.connection_manager import connection_manager

logger = get_logger(__name__)


class DatabaseCrawler:
    """Core component that crawls database tables and retrieves information"""

    def __init__(self, config_parser: ConfigParser):
        self.config_parser = config_parser

    async def get_available_tables(self, db: Session) -> List[str]:
        """Get list of all available tables in the database"""
        source_name = self.config_parser.get_source_name()

        try:
            tables = await connection_manager.list_tables(db, source_name)
            table_names = []

            for table in tables:
                # Create full table name including schema if available
                if table.schema_name:
                    full_name = f"{table.schema_name}.{table.name}"
                else:
                    full_name = table.name
                table_names.append(full_name)

            logger.info(f"Found {len(table_names)} tables in source {source_name}")
            return table_names

        except Exception as e:
            logger.error(f"Failed to get available tables from {source_name}: {str(e)}")
            return []

    async def get_table_ddl(self, db: Session, table_name: str, schema_name: Optional[str] = None) -> str:
        """Get DDL (CREATE TABLE statement) for a table"""
        source_name = self.config_parser.get_source_name()
        engine = await connection_manager.get_engine(db, source_name)

        if not engine:
            raise Exception(f"Could not get database engine for source {source_name}")

        try:
            with engine.connect() as conn:
                # For SQLite, we can get DDL from sqlite_master
                if "sqlite" in str(engine.url):
                    query = text("SELECT sql FROM sqlite_master WHERE type='table' AND name=:table_name")
                    result = conn.execute(query, {"table_name": table_name})
                    row = result.fetchone()
                    if row and row[0]:
                        return row[0]
                else:
                    # For other databases, we'll construct a simple DDL from column info
                    columns = await connection_manager.get_table_columns(db, source_name, table_name, schema_name)
                    if not columns:
                        return f"-- DDL not available for table {table_name}"

                    # Build basic CREATE TABLE statement
                    ddl_parts = [f"CREATE TABLE {table_name} ("]
                    column_defs = []

                    for col in columns:
                        col_def = f"  {col.name} {col.type}"
                        if not col.nullable:
                            col_def += " NOT NULL"
                        if col.default:
                            col_def += f" DEFAULT {col.default}"
                        column_defs.append(col_def)

                    ddl_parts.append(",\n".join(column_defs))
                    ddl_parts.append(");")
                    return "\n".join(ddl_parts)

        except Exception as e:
            logger.error(f"Failed to get DDL for table {table_name}: {str(e)}")
            return f"-- DDL retrieval failed for table {table_name}: {str(e)}"

    async def get_sample_data(
        self, db: Session, table_name: str, table_spec: Union[TableSelection, TableRegexSelection], schema_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get sample data from a table"""
        source_name = self.config_parser.get_source_name()
        engine = await connection_manager.get_engine(db, source_name)

        if not engine:
            raise Exception(f"Could not get database engine for source {source_name}")

        try:
            with engine.connect() as conn:
                # Use custom sample query if provided
                custom_query = self.config_parser.get_custom_sample_query(table_spec)
                if custom_query:
                    logger.info(f"Using custom sample query for table {table_name}")
                    result = conn.execute(text(custom_query))
                else:
                    # Build default sample query
                    columns = self.config_parser.get_effective_columns(table_spec)
                    sample_rows = self.config_parser.get_effective_sample_rows(table_spec)

                    if columns:
                        # Select specific columns
                        column_list = ", ".join(columns)
                        query = f"SELECT {column_list} FROM {table_name}"
                    else:
                        # Select all columns
                        query = f"SELECT * FROM {table_name}"

                    # Add filtering for non-null values and LIMIT
                    if columns:
                        # Build WHERE clause to filter out rows where all selected columns are NULL
                        non_null_conditions = [f"{col} IS NOT NULL" for col in columns]
                        where_clause = " OR ".join(non_null_conditions)
                        query += f" WHERE {where_clause}"

                    query += f" LIMIT {sample_rows}"

                    logger.info(f"Executing sample query for table {table_name}: {query}")
                    result = conn.execute(text(query))

                # Convert result to list of dictionaries
                columns = list(result.keys())
                sample_data = []

                for row in result:
                    row_dict = {}
                    for i, col_name in enumerate(columns):
                        value = row[i]
                        # Convert value to JSON-serializable format
                        if value is None:
                            row_dict[col_name] = None
                        else:
                            # Convert to string to ensure JSON serialization
                            row_dict[col_name] = str(value)
                    sample_data.append(row_dict)

                logger.info(f"Retrieved {len(sample_data)} sample rows from table {table_name}")
                return sample_data

        except Exception as e:
            logger.error(f"Failed to get sample data from table {table_name}: {str(e)}")
            return []

    async def crawl_table(self, db: Session, table_name: str, table_spec: Union[TableSelection, TableRegexSelection]) -> Dict[str, Any]:
        """Crawl a single table and return its information"""
        logger.info(f"Crawling table: {table_name}")

        # Parse schema and table name
        schema_name = None
        clean_table_name = table_name

        if "." in table_name:
            parts = table_name.split(".", 1)
            schema_name = parts[0]
            clean_table_name = parts[1]

        try:
            # Get DDL
            ddl = await self.get_table_ddl(db, clean_table_name, schema_name)

            # Get sample data
            sample_data = await self.get_sample_data(db, table_name, table_spec, schema_name)

            return {"table_name": clean_table_name, "full_path": table_name, "ddl": ddl, "sample_data": sample_data, "schema_name": schema_name}

        except Exception as e:
            logger.error(f"Failed to crawl table {table_name}: {str(e)}")
            raise Exception(f"Table crawl failed for {table_name}: {str(e)}")

    async def crawl_all_tables(self, db: Session) -> List[Dict[str, Any]]:
        """Crawl all configured tables"""
        # Get available tables
        available_tables = await self.get_available_tables(db)
        if not available_tables:
            raise Exception("No tables found in the database")

        # Resolve table specifications
        resolved_tables = self.config_parser.resolve_table_selection(available_tables)
        if not resolved_tables:
            raise Exception("No tables matched the configuration specifications")

        logger.info(f"Will crawl {len(resolved_tables)} tables")

        # Crawl each table
        crawled_tables = []
        for table_name, table_spec in resolved_tables:
            try:
                table_info = await self.crawl_table(db, table_name, table_spec)
                crawled_tables.append(table_info)
            except Exception as e:
                logger.error(f"Failed to crawl table {table_name}: {str(e)}")
                # Continue with other tables even if one fails
                continue

        if not crawled_tables:
            raise Exception("Failed to crawl any tables")

        logger.info(f"Successfully crawled {len(crawled_tables)} tables")
        return crawled_tables
