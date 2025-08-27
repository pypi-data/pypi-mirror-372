"""
Data exploration service

This module provides business logic for data exploration and discovery,
including schema listing for both SQL databases and Kafka clusters.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import anyio
from fastmcp import Context
from sqlalchemy.orm import Session

from resinkit_api.core.logging import get_logger
from resinkit_api.db import data_sources_crud
from resinkit_api.services.agent.db_crawl.models import DbCrawlConfig, TableSelection
from resinkit_api.services.agent.db_crawl.service import DatabaseCrawlService
from resinkit_api.services.agent.kafka_crawl.models import (
    AnalysisConfig,
    DefaultSettings,
    KafkaCrawlConfig,
    KafkaSource,
    SamplingStrategy,
    SchemaInferenceConfig,
    TopicRegexSelection,
    ValueDeserializer,
)
from resinkit_api.services.agent.kafka_crawl.service import KafkaCrawlService
from resinkit_api.services.agent.sql_tools.connection_manager import connection_manager
from resinkit_api.services.flink_session_service import FlinkSessionService
from resinkit_api.services.flink_sql_execution_service import FlinkSQLExecutionService

logger = get_logger(__name__)


class DataExplorerService:
    """Service for data exploration and schema discovery"""

    def __init__(self, flink_session_service: FlinkSessionService = None) -> None:
        """Initialize the data explorer service"""
        self.flink_session_service = flink_session_service
        if self.flink_session_service:
            self.flink_sql_service = FlinkSQLExecutionService(self.flink_session_service)
        else:
            self.flink_sql_service = None

    async def list_data_sources(self, db) -> List[Dict[str, Any]]:
        """
        List all registered data sources available for querying.

        Args:
            db: Database session

        Returns:
            List of data sources with their metadata
        """
        sources = await data_sources_crud.list_data_sources(db)

        # Format response without sensitive data
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

        return sources_data

    async def get_data_source_schemas(self, db, source_name: str, sample_count: int) -> Dict[str, Any]:
        """
        Retrieve descriptive sample data schemas for all data entities in a specified data source.

        This method supports multiple data source types including SQL databases, Kafka clusters,
        and other data systems. It analyzes sample data to generate DSDS (Descriptive Sample
        Data Schema) strings that describe the structure, types, and characteristics of data.

        Args:
            db: Database session
            source_name: Data source name (SQL database, Kafka cluster, or other data source)
            sample_count: Number of sample rows/messages to retrieve for schema analysis

        Returns:
            Dictionary with schemas, total_entities, source_type, and optional error
        """
        # Get the data source to determine its type
        source = await data_sources_crud.get_data_source(db, source_name)
        if not source:
            return {"schemas": [], "total_entities": 0, "source_type": "unknown", "error": f"Data source '{source_name}' not found"}

        # Check if this is a Kafka source (assuming Kafka sources have kind 'kafka')
        if source.kind.lower() == "kafka":
            # Note: get_data_source_schemas doesn't have ctx parameter, so pass None
            result = await self._list_kafka_topic_schemas(source_name, source, sample_count, ctx=None)
            result["source_type"] = "kafka"
            return result
        else:
            result = await self._list_sql_table_schemas(db, source_name, sample_count)
            result["source_type"] = "sql"
            return result

    async def _list_sql_table_schemas(self, db, source_name: str, sample_count: int) -> Dict[str, Any]:
        """Handle SQL database table schema listing"""
        # Create crawl config for all tables (no table specification = crawl all)
        crawl_config = DbCrawlConfig(
            source=source_name,
            defaults={"sample_rows": sample_count},
            tables=None,  # This will crawl all tables
            dsds={"generate": True, "include_examples": True},
        )

        # Execute crawl
        service = DatabaseCrawlService()
        result = await service.execute_crawl(db, crawl_config, save_remote=False)

        # Extract only the DSDS strings
        schemas = [table.dsds for table in result.tables if table.dsds]

        return {"schemas": schemas, "total_entities": len(schemas)}

    async def _list_kafka_topic_schemas(self, source_name: str, source, sample_count: int, ctx: Optional[Context] = None) -> Dict[str, Any]:
        """Handle Kafka topic schema listing with progress reporting"""
        try:
            # Report initial progress
            if ctx:
                try:
                    await ctx.report_progress(progress=10, total=100, message=f"Starting Kafka topic crawl for {source_name}")
                except (anyio.ClosedResourceError, anyio.BrokenResourceError):
                    return {"schemas": [], "total_entities": 0, "error": "Operation cancelled due to client disconnection"}

            # For Kafka data sources, bootstrap_servers comes from extra_params
            if not source.extra_params or not source.extra_params.get("bootstrap.servers"):
                return {"schemas": [], "total_entities": 0, "error": f"Kafka data source '{source_name}' requires 'bootstrap.servers' in extra_params"}

            # Create Kafka source configuration
            kafka_source = KafkaSource(
                bootstrap_servers=source.extra_params.get("bootstrap.servers"),
                security_protocol=source.extra_params.get("security_protocol") if source.extra_params else None,
                sasl_mechanism=source.extra_params.get("sasl_mechanism") if source.extra_params else None,
                sasl_username=source.extra_params.get("sasl.username") if source.extra_params else None,
                sasl_password=source.extra_params.get("sasl.password") if source.extra_params else None,
            )

            # Create default settings
            defaults = DefaultSettings(
                sample_messages=sample_count,  # Use sample_count as sample_messages count
                sampling_strategy=SamplingStrategy.LATEST_OFFSET,  # Use latest_offset to get recent messages
                consumer_timeout_ms=10000,  # 10 second timeout
            )

            # Create topic regex selection to match all topics except internal ones
            topic_selection = TopicRegexSelection(
                name_regex="^(?!__).*",  # Match all topics that don't start with '__'
                value_deserializer=ValueDeserializer.JSON,
                sample_messages=None,  # Use default
                sampling_strategy=None,  # Use default
            )

            # Create schema inference config
            schema_inference = SchemaInferenceConfig(
                generate=True,
                include_examples=True,
                max_examples_per_field=3,
                analysis=AnalysisConfig(
                    calculate_null_percentage=True,
                    estimate_cardinality=True,
                ),
            )

            # Create Kafka crawl config
            kafka_config = KafkaCrawlConfig(
                kafka_source=kafka_source,
                defaults=defaults,
                topics=[topic_selection],
                schema_inference=schema_inference,
            )

            # Report crawl start progress
            if ctx:
                try:
                    await ctx.report_progress(progress=30, total=100, message="Connecting to Kafka cluster and discovering topics")
                except (anyio.ClosedResourceError, anyio.BrokenResourceError):
                    return {"schemas": [], "total_entities": 0, "error": "Operation cancelled due to client disconnection"}

            # Execute Kafka crawl
            kafka_service = KafkaCrawlService()
            result = await kafka_service.execute_crawl(kafka_config)

            # Report crawl completion progress
            if ctx:
                try:
                    await ctx.report_progress(progress=70, total=100, message="Processing topic schemas")
                except (anyio.ClosedResourceError, anyio.BrokenResourceError):
                    return {"schemas": [], "total_entities": 0, "error": "Operation cancelled due to client disconnection"}

            # Convert Kafka results to DSDS format
            schemas = []
            total_topics = len(result.topics)

            for i, topic_result in enumerate(result.topics):
                # Report conversion progress
                if ctx and total_topics > 0:
                    try:
                        conversion_progress = 70 + int((i / total_topics) * 25)  # 70-95% range
                        await ctx.report_progress(
                            progress=conversion_progress, total=100, message=f"Converting schema for topic {topic_result.topic_name} ({i+1}/{total_topics})"
                        )
                    except (anyio.ClosedResourceError, anyio.BrokenResourceError):
                        return {"schemas": [], "total_entities": 0, "error": "Operation cancelled due to client disconnection"}

                if topic_result.field_analysis:
                    dsds = self._convert_kafka_analysis_to_dsds(topic_result.topic_name, topic_result.field_analysis)
                    schemas.append(dsds)
                else:
                    # If no field analysis, create basic DSDS
                    schemas.append(f"topic: {topic_result.topic_name}\nNo field analysis available")

            # Report completion
            if ctx:
                try:
                    await ctx.report_progress(progress=100, total=100, message=f"Kafka schema crawl completed - found {len(schemas)} topics")
                except (anyio.ClosedResourceError, anyio.BrokenResourceError):
                    # Task is complete, don't need to return error
                    pass

            return {"schemas": schemas, "total_entities": len(schemas)}

        except Exception as e:
            logger.error(f"Failed to crawl Kafka topics for {source_name}: {str(e)}", exc_info=True)
            return {"schemas": [], "total_entities": 0, "error": f"Failed to crawl Kafka topics: {str(e)}"}

    def _convert_kafka_analysis_to_dsds(self, topic_name: str, field_analysis: dict) -> str:
        """Convert Kafka field analysis to DSDS format string"""
        if not field_analysis:
            return f"topic: {topic_name}\nNo field analysis available"

        dsds_lines = [f"topic: {topic_name}"]

        for field_name, analysis in field_analysis.items():
            # Extract analysis data - analysis is a KafkaFieldAnalysis object, not a dict
            inferred_type = analysis.inferred_type if analysis.inferred_type else "unknown"
            examples = analysis.examples if analysis.examples else []
            analysis_data = analysis.analysis if analysis.analysis else {}

            # Get statistics from analysis
            null_percentage = analysis_data.get("null_percentage", 0)
            cardinality = analysis_data.get("cardinality", "unknown")

            # Format examples (limit to 3 for readability)
            example_str = ", ".join(str(ex) for ex in examples[:3])

            # Build field line in DSDS format
            field_line = f"<field> {field_name}:{inferred_type}"

            if examples:
                field_line += f", Examples: [{example_str}]"

            field_line += f", null_percentage:{null_percentage}"

            if cardinality != "unknown":
                field_line += f", cardinality: {cardinality}"

            field_line += " </field>"
            dsds_lines.append(field_line)

        return "\n".join(dsds_lines)

    async def get_schema_with_query(self, db, source_name: str, query: str, table_name: str) -> Dict[str, Any]:
        """
        Get the schema for a custom SQL query.

        This method executes a custom SQL query and generates a DSDS (Descriptive Sample Data Schema)
        for the result set. This is useful for understanding the structure and sample data
        of complex queries, joins, or specific column selections.

        Args:
            db: Database session
            source_name: SQL source name (configured via /sources endpoints)
            query: SQL query to execute for schema generation
            table_name: Name to use for the resulting schema

        Returns:
            Dictionary with schema and optional error
        """
        # Create a table selection with custom sample query
        table_selection = TableSelection(name=table_name, sample_query=query)

        # Create crawl config with the custom query
        crawl_config = DbCrawlConfig(
            source=source_name,
            defaults={"sample_rows": 10},  # Default sample rows for query results
            tables=[table_selection],
            dsds={"generate": True, "include_examples": True},
        )

        # Execute crawl
        service = DatabaseCrawlService()
        result = await service.execute_crawl(db, crawl_config, save_remote=False)

        # Extract the DSDS string
        if result.tables and result.tables[0].dsds:
            schema = result.tables[0].dsds
        else:
            schema = "No schema generated - query may have failed or returned no results"

        return {"schema": schema}

    async def get_sql_schema_with_query(self, db, source_name: str, query: str, table_name: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
        """
        Get the schema for a custom SQL query with SQL compatibility validation.

        This method validates that the data source supports SQL queries before executing
        the schema generation. Returns appropriate error messages for incompatible data sources.

        Args:
            db: Database session
            source_name: Data source name
            query: SQL query to execute for schema generation
            table_name: Name to use for the resulting schema
            ctx: FastMCP context for progress reporting and cancellation detection

        Returns:
            Dictionary with schema and optional error, including compatibility validation
        """
        from resinkit_api.services.agent.sql_tools.models import DatabaseKind

        # Check if data source exists
        source = await data_sources_crud.get_data_source(db, source_name)
        if not source:
            return {"schema": "", "error": f"Data source '{source_name}' not found"}

        # If kafka, fallback to kafka schema generation with fixed sample count
        if DatabaseKind(source.kind) == DatabaseKind.KAFKA:
            result = await self._list_kafka_topic_schemas(source_name, source, 3, ctx=ctx)
            result["source_type"] = "kafka"
            return result

        # Proceed with schema generation for SQL-compatible sources
        return await self.get_schema_with_query(db, source_name, query, table_name)

    async def execute_sql_query_with_validation(self, db, source_name: Optional[str], query: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
        """
        Execute a SQL query with SQL compatibility validation.

        This method validates that the data source supports SQL queries before executing
        the query. If no source is specified or the source is of Kafka kind, it uses Flink SQL.

        Args:
            db: Database session
            source_name: Optional data source name. If None or Kafka kind, uses Flink SQL
            query: SQL query to execute
            ctx: FastMCP context for progress reporting and cancellation detection

        Returns:
            Dictionary with query results and optional error, including compatibility validation
        """
        from resinkit_api.services.agent.sql_tools.models import DatabaseKind

        # If no source specified, use Flink SQL
        if not source_name:
            return await self._execute_flink_sql(
                db=db,
                source_name="flink_default",
                query=query,
                task_name="Flink SQL query (no source specified)",
                timeout_seconds=300,
                ctx=ctx,
            )

        # Check if data source exists
        source = await data_sources_crud.get_data_source(db, source_name)
        if not source or source.kind == DatabaseKind.KAFKA:
            return await self._execute_flink_sql(
                db=db,
                source_name=source_name,
                query=query,
                task_name=f"Flink SQL query for {source_name}",
                timeout_seconds=300,
                ctx=ctx,
            )

        # Proceed with query execution for SQL-compatible sources
        return await self._execute_sql_query(db, source_name, query, ctx)

    async def _execute_flink_sql(
        self,
        db: Session,
        source_name: str,
        query: str,
        task_name: str,
        timeout_seconds: int,
        ctx: Optional[Context] = None,
    ) -> Dict[str, Any]:
        """
        Execute a Flink SQL query against a Kafka data source using FlinkSQLExecutionService.

        This method uses the streaming SQL execution service to run Flink SQL queries,
        with client disconnection detection and graceful cancellation.

        Args:
            source_name: Kafka data source name
            query: Flink SQL query to execute
            task_name: Name for the task (used for logging)
            timeout_seconds: Maximum wait time in seconds
            ctx: FastMCP context for progress reporting and cancellation detection

        Returns:
            Dictionary with formatted results and optional error
        """
        session_id = None
        try:
            session_id = await self.flink_session_service.open_session(session_name=source_name)
            if not session_id:
                return {
                    "columns": [],
                    "rows": [],
                    "row_count": 0,
                    "execution_time_ms": 0.0,
                    "error": f"Failed to create Flink session for {source_name}",
                    "error_type": "session_error",
                    "troubleshooting_tips": "Could not establish a Flink session. Check Flink cluster connectivity and configuration.",
                }

            logger.info(f"Executing Flink SQL query using session {session_id}: {task_name}")
            start_time = datetime.now()

            # Report initial progress
            if ctx:
                try:
                    await ctx.report_progress(progress=10, total=100, message="Starting Flink SQL query")
                except (anyio.ClosedResourceError, anyio.BrokenResourceError):
                    return self._format_cancellation_response()

            # Collect results from streaming execution
            results = []
            columns = []
            last_progress = 10

            try:
                async for response in self.flink_sql_service.execute_sql_streaming(
                    session_id=session_id,
                    sql=query,
                    execution_timeout=timeout_seconds,
                    poll_interval_secs=0.5,
                    max_poll_secs=timeout_seconds,
                    n_row_limit=10000,  # Reasonable limit for data exploration
                    db=db,
                ):
                    # Check for client disconnection
                    if ctx:
                        try:
                            # Update progress based on streaming results
                            if response.fetch_result.eos:
                                progress = 90
                            else:
                                progress = min(last_progress + 10, 80)
                                last_progress = progress

                            await ctx.report_progress(progress=progress, total=100, message="Processing Flink SQL results")
                        except (anyio.ClosedResourceError, anyio.BrokenResourceError):
                            # Client disconnected - we should stop processing
                            logger.info("Client disconnected during Flink SQL streaming execution")
                            return self._format_cancellation_response()

                    # Process the streaming response
                    if response.fetch_result.data:
                        results.extend(response.fetch_result.data)

                    # Extract column information on first response
                    if not columns and response.fetch_result.columns:
                        columns = [col.name for col in response.fetch_result.columns]

                    # Break if we've reached the end of the stream
                    if response.fetch_result.eos:
                        break

                # Calculate execution time
                execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000

                # Report completion
                if ctx:
                    try:
                        await ctx.report_progress(progress=100, total=100, message="Flink SQL query completed")
                    except (anyio.ClosedResourceError, anyio.BrokenResourceError):
                        logger.info("Client disconnected at completion, but results are available")

                return {
                    "columns": columns,
                    "rows": results,
                    "row_count": len(results),
                    "execution_time_ms": execution_time_ms,
                }

            except Exception as stream_error:
                logger.error(f"Error during Flink SQL streaming: {str(stream_error)}", exc_info=True)
                execution_time_ms = (datetime.now() - start_time).total_seconds() * 1000

                # Analyze error for better troubleshooting
                error_str = str(stream_error).lower()
                error_type = "execution_error"
                troubleshooting_tips = "The Flink SQL query failed to execute."

                if "timeout" in error_str:
                    error_type = "timeout_error"
                    troubleshooting_tips = "Query timed out. Consider adding filters to reduce data volume or increase timeout."
                elif "table" in error_str and "not found" in error_str:
                    error_type = "table_not_found"
                    troubleshooting_tips = "Table or topic not found. Verify the table/topic name and Flink SQL environment setup."
                elif "syntax" in error_str or "parse" in error_str or "SQL validation failed" in error_str:
                    error_type = "syntax_error"
                    troubleshooting_tips = "SQL syntax error. Check Flink SQL syntax and table references."
                return {
                    "columns": [],
                    "rows": [],
                    "row_count": 0,
                    "execution_time_ms": execution_time_ms,
                    "error": f"Flink SQL query failed: {str(stream_error)}",
                    "error_type": error_type,
                    "troubleshooting_tips": troubleshooting_tips,
                }

        except Exception as e:
            logger.error(f"Error executing Flink SQL query: {str(e)}", exc_info=True)
            return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": 0.0,
                "error": f"Error executing Flink SQL query: {str(e)}",
                "error_type": "internal_error",
                "troubleshooting_tips": "An internal error occurred while executing the Flink SQL query. Check the application logs for more details.",
            }
        finally:
            if session_id:
                await self.flink_session_service.close_session(session_id)

    def _format_cancellation_response(self) -> Dict[str, Any]:
        """Format a cancellation response based on result type."""
        return {
            "columns": [],
            "rows": [],
            "row_count": 0,
            "execution_time_ms": 0.0,
            "error": "Query cancelled due to client disconnection",
            "error_type": "client_disconnected",
            "troubleshooting_tips": "The client disconnected while the query was executing.",
        }

    async def _execute_sql_query(self, db, source_name: str, query: str, ctx: Optional[Context] = None) -> Dict[str, Any]:
        """
        Execute a SQL query against a specified data source.

        This method executes SQL queries with comprehensive error handling and provides
        detailed troubleshooting information when queries fail. Supports client disconnection
        detection for better user experience.

        Args:
            db: Database session
            source_name: SQL source name (configured via /sources endpoints)
            query: SQL query to execute
            ctx: FastMCP context for progress reporting and cancellation detection

        Returns:
            Dictionary with query results or detailed error information
        """
        # Check if source exists
        source = await data_sources_crud.get_data_source(db, source_name)
        if not source:
            return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": 0.0,
                "error": f"SQL source '{source_name}' not found",
                "error_type": "source_not_found",
                "troubleshooting_tips": "Check if the source name is correct and that the data source has been properly configured via the /sources endpoints. Use list_data_sources tool to see available sources.",
            }

        # Execute query using connection manager
        try:
            # Report progress if context is available
            if ctx:
                try:
                    await ctx.report_progress(progress=50, total=100, message=f"Executing SQL query on {source_name}")
                except (anyio.ClosedResourceError, anyio.BrokenResourceError):
                    # Client disconnected before execution
                    return {
                        "columns": [],
                        "rows": [],
                        "row_count": 0,
                        "execution_time_ms": 0.0,
                        "error": "Query cancelled due to client disconnection",
                        "error_type": "client_disconnected",
                        "troubleshooting_tips": "The client disconnected before the query could be executed.",
                    }

            result = await connection_manager.execute_query(db, source_name, query)

            # Report completion if context is available
            if ctx:
                try:
                    await ctx.report_progress(progress=100, total=100, message="SQL query completed")
                except (anyio.ClosedResourceError, anyio.BrokenResourceError):
                    # Client disconnected after execution, but we'll still return results
                    logger.info("Client disconnected after SQL query completion, but results are available")

            if result is None:
                return {
                    "columns": [],
                    "rows": [],
                    "row_count": 0,
                    "execution_time_ms": 0.0,
                    "error": "Failed to execute query - connection error",
                    "error_type": "connection_error",
                    "troubleshooting_tips": "The database connection could not be established. Check if the database server is running, network connectivity is available, and the connection parameters (host, port, credentials) are correct.",
                }

            # Return successful result
            return {
                "columns": result.columns,
                "rows": result.rows,
                "row_count": result.row_count,
                "execution_time_ms": result.execution_time_ms,
            }

        except (anyio.ClosedResourceError, anyio.BrokenResourceError):
            # Client disconnection detected during query execution
            return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": 0.0,
                "error": "Query cancelled due to client disconnection",
                "error_type": "client_disconnected",
                "troubleshooting_tips": "The client disconnected while the query was executing.",
            }
        except Exception as query_error:
            # Analyze error type and provide specific troubleshooting tips
            error_str = str(query_error).lower()
            error_type = "unknown_error"
            troubleshooting_tips = "An unexpected error occurred during query execution."

            # SQL syntax errors
            if any(keyword in error_str for keyword in ["syntax error", "parse error", "invalid syntax", "near", "unexpected"]):
                error_type = "syntax_error"
                troubleshooting_tips = "SQL syntax error detected. Check for: missing commas, unmatched quotes, misspelled keywords, incorrect table/column names, or unsupported SQL features for this database type."

            # Table/column not found errors
            elif any(keyword in error_str for keyword in ["table", "doesn't exist", "not found", "unknown table", "no such table"]):
                error_type = "table_not_found"
                troubleshooting_tips = "Table not found. Verify the table name is correct, check if you need to specify a schema (e.g., schema.table), and ensure you have access to the table. Use list_table_schemas tool to see available tables."

            elif any(keyword in error_str for keyword in ["column", "unknown column", "no such column", "invalid column"]):
                error_type = "column_not_found"
                troubleshooting_tips = "Column not found. Check if the column name is spelled correctly, verify it exists in the specified table, and ensure proper quoting if needed. Use get_schema_with_query tool to see available columns."

            # Permission errors
            elif any(keyword in error_str for keyword in ["access denied", "permission", "forbidden", "not authorized", "privilege"]):
                error_type = "permission_error"
                troubleshooting_tips = "Access denied. The database user may lack permissions for this operation. Check if you have SELECT/INSERT/UPDATE/DELETE privileges on the target tables, or contact your database administrator."

            # Connection/timeout errors
            elif any(keyword in error_str for keyword in ["timeout", "connection", "network", "host", "unreachable"]):
                error_type = "connection_error"
                troubleshooting_tips = "Connection or timeout error. Check network connectivity, verify the database server is running, ensure firewall rules allow connections, and consider increasing query timeout if needed."

            # Data type errors
            elif any(keyword in error_str for keyword in ["type", "conversion", "cast", "invalid", "format"]):
                error_type = "data_type_error"
                troubleshooting_tips = "Data type error. Check for type mismatches in comparisons, invalid date/number formats, or incompatible operations between different data types."

            # Resource/limit errors
            elif any(keyword in error_str for keyword in ["memory", "disk", "space", "limit", "quota", "too large"]):
                error_type = "resource_error"
                troubleshooting_tips = "Resource limit exceeded. The query may be returning too much data or using too much memory. Try adding LIMIT clauses, optimizing joins, or breaking the query into smaller parts."

            return {
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": 0.0,
                "error": f"Query execution failed: {str(query_error)}",
                "error_type": error_type,
                "troubleshooting_tips": troubleshooting_tips,
            }
