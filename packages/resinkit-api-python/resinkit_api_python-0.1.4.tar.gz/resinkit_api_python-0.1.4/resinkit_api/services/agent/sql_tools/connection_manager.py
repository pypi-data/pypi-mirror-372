import time
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

from aiokafka import AIOKafkaProducer
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from resinkit_api.core.config import settings
from resinkit_api.core.logging import get_logger
from resinkit_api.db.data_sources_crud import get_data_source, get_decrypted_credentials
from resinkit_api.services.agent.sql_tools.models import (
    ColumnInfo,
    DatabaseInfo,
    DatabaseKind,
    DataSourceConnectionTestResult,
    DataSourceQueryResult,
    SchemaInfo,
    TableInfo,
)

logger = get_logger(__name__)


class SqlConnectionManager:
    """Manages SQL database connections and operations"""

    def __init__(self):
        self._engines: Dict[str, Engine] = {}

    def _get_connection_url(
        self,
        source_name: str,
        kind: DatabaseKind,
        host: Optional[str],
        port: Optional[int],
        database: str,
        user: Optional[str],
        password: Optional[str],
        extra_params: Optional[Dict[str, Any]],
    ) -> str:
        """Build database connection URL"""

        if kind == DatabaseKind.SQLITE:
            # SQLite doesn't use host/port/user/password
            # Check if this is a filename from SQLITE_FOLDER or an absolute path
            if database.endswith(".sqlite") and not database.startswith("/"):
                # This is a filename, resolve to full path in SQLITE_FOLDER
                full_path = settings.SQLITE_FOLDER_PATH / database
                url = f"sqlite:///{full_path}"
            else:
                # This is already a full path or doesn't follow our naming convention
                url = f"sqlite:///{database}"
        elif kind == DatabaseKind.KAFKA:
            # Kafka doesn't use traditional SQL connection - bootstrap servers are in extra_params
            if not extra_params or not extra_params.get("bootstrap.servers"):
                raise ValueError("Kafka data sources require 'bootstrap.servers' in extra_params")
            # For Kafka, we'll create a pseudo-URL since we don't actually use SQLAlchemy
            # The actual connection handling will be done by Kafka libraries
            bootstrap_servers = extra_params.get("bootstrap.servers")
            url = f"kafka://{bootstrap_servers}"
            if database:
                url += f"/{database}"  # database represents the topic name
        else:
            # For traditional SQL databases, require host, port, user, password
            if not all([host, port, user, password]):
                raise ValueError(f"Host, port, user, and password are required for {kind} databases")

            # URL encode credentials
            encoded_user = quote_plus(user)
            encoded_password = quote_plus(password)

            if kind == DatabaseKind.MYSQL:
                url = f"mysql+pymysql://{encoded_user}:{encoded_password}@{host}:{port}/{database}"
            elif kind == DatabaseKind.POSTGRESQL:
                url = f"postgresql+psycopg2://{encoded_user}:{encoded_password}@{host}:{port}/{database}"
            elif kind == DatabaseKind.MSSQL:
                url = f"mssql+pymssql://{encoded_user}:{encoded_password}@{host}:{port}/{database}"
            elif kind == DatabaseKind.ORACLE:
                url = f"oracle+cx_oracle://{encoded_user}:{encoded_password}@{host}:{port}/{database}"
            else:
                raise ValueError(f"Unsupported database kind: {kind}")

        # Add extra parameters to URL
        if extra_params:
            param_str = "&".join([f"{k}={v}" for k, v in extra_params.items()])
            url += f"?{param_str}"

        return url

    async def get_engine(self, db: Session, source_name: str) -> Optional[Engine]:
        """Get or create database engine for a SQL source"""

        # Check if engine already exists
        if source_name in self._engines:
            return self._engines[source_name]

        # Get source configuration
        data_source = await get_data_source(db, source_name)
        if not data_source:
            logger.error(f"SQL source not found: {source_name}")
            return None

        # Kafka is not a SQL database - don't create SQLAlchemy engine
        if DatabaseKind(data_source.kind) == DatabaseKind.KAFKA:
            logger.error(f"Kafka data source {source_name} should not use SQLAlchemy engine")
            return None

        # Get decrypted credentials (may be empty for SQLite)
        credentials = await get_decrypted_credentials(db, source_name) or {}

        # For SQLite, credentials are not required
        is_sqlite = DatabaseKind(data_source.kind) == DatabaseKind.SQLITE
        if not is_sqlite and not credentials:
            logger.error(f"Failed to get credentials for SQL source: {source_name}")
            return None

        try:
            # Build connection URL
            connection_url = self._get_connection_url(
                source_name=source_name,
                kind=DatabaseKind(data_source.kind),
                host=data_source.host,
                port=data_source.port,
                database=data_source.database,
                user=credentials.get("user"),
                password=credentials.get("password"),
                extra_params=data_source.get_extra_params(),
            )

            # Create engine
            engine = create_engine(connection_url, echo=False)

            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            # Cache engine
            self._engines[source_name] = engine
            logger.info(f"Created database engine for source: {source_name}")

            return engine

        except Exception as e:
            logger.error(f"Failed to create database engine for {source_name}: {str(e)}")
            return None

    async def list_databases(self, db: Session, source_name: str) -> List[DatabaseInfo]:
        """List databases in a SQL source"""
        # Get source info to determine database type
        data_source = await get_data_source(db, source_name)
        if not data_source:
            return []

        kind = DatabaseKind(data_source.kind)

        # Handle Kafka differently - return topics as "databases"
        if kind == DatabaseKind.KAFKA:
            # For Kafka, we could list topics here if we had Kafka client
            # For now, return the configured database/topic name
            if data_source.database:
                return [DatabaseInfo(name=data_source.database)]
            else:
                # Empty database means all topics - return a placeholder
                return [DatabaseInfo(name="all_topics")]

        # Handle SQL databases
        engine = await self.get_engine(db, source_name)
        if not engine:
            return []

        try:
            with engine.connect() as conn:
                inspector = inspect(engine)

                if kind in [DatabaseKind.MYSQL, DatabaseKind.STARROCKS]:
                    result = conn.execute(text("SHOW DATABASES"))
                    databases = [DatabaseInfo(name=row[0]) for row in result]
                elif kind == DatabaseKind.POSTGRESQL:
                    result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false"))
                    databases = [DatabaseInfo(name=row[0]) for row in result]
                elif kind == DatabaseKind.SQLITE:
                    # SQLite has only one database
                    databases = [DatabaseInfo(name=data_source.database)]
                elif kind == DatabaseKind.MSSQL:
                    result = conn.execute(text("SELECT name FROM sys.databases"))
                    databases = [DatabaseInfo(name=row[0]) for row in result]
                else:
                    # Fallback: try to get from inspector
                    database_names = inspector.get_schema_names()
                    databases = [DatabaseInfo(name=name) for name in database_names]

                return databases

        except Exception as e:
            logger.error(f"Failed to list databases for {source_name}: {str(e)}")
            return []

    async def list_schemas(self, db: Session, source_name: str, database_name: Optional[str] = None) -> List[SchemaInfo]:
        """List schemas in a database"""
        # Get source info to determine database type
        data_source = await get_data_source(db, source_name)
        if not data_source:
            return []

        kind = DatabaseKind(data_source.kind)

        # Kafka doesn't have schemas
        if kind == DatabaseKind.KAFKA:
            return []

        engine = await self.get_engine(db, source_name)
        if not engine:
            return []

        try:
            with engine.connect():
                inspector = inspect(engine)
                schema_names = inspector.get_schema_names()
                return [SchemaInfo(name=name) for name in schema_names]

        except Exception as e:
            logger.error(f"Failed to list schemas for {source_name}: {str(e)}")
            return []

    async def list_tables(self, db: Session, source_name: str, schema_name: Optional[str] = None) -> List[TableInfo]:
        """List tables in a schema"""
        # Get source info to determine database type
        data_source = await get_data_source(db, source_name)
        if not data_source:
            return []

        kind = DatabaseKind(data_source.kind)

        # Kafka doesn't have tables - return empty list or could list partitions
        if kind == DatabaseKind.KAFKA:
            return []

        engine = await self.get_engine(db, source_name)
        if not engine:
            return []

        try:
            with engine.connect():
                inspector = inspect(engine)

                # Get table names
                table_names = inspector.get_table_names(schema=schema_name)
                tables = [TableInfo(name=name, schema_name=schema_name, type="table") for name in table_names]

                # Get view names if supported
                try:
                    view_names = inspector.get_view_names(schema=schema_name)
                    tables.extend([TableInfo(name=name, schema_name=schema_name, type="view") for name in view_names])
                except Exception:
                    # Views might not be supported for all databases
                    pass

                return tables

        except Exception as e:
            logger.error(f"Failed to list tables for {source_name}: {str(e)}")
            return []

    async def get_table_columns(self, db: Session, source_name: str, table_name: str, schema_name: Optional[str] = None) -> List[ColumnInfo]:
        """Get columns for a table"""
        # Get source info to determine database type
        data_source = await get_data_source(db, source_name)
        if not data_source:
            return []

        kind = DatabaseKind(data_source.kind)

        # Kafka doesn't have table columns
        if kind == DatabaseKind.KAFKA:
            return []

        engine = await self.get_engine(db, source_name)
        if not engine:
            return []

        try:
            with engine.connect():
                inspector = inspect(engine)
                columns = inspector.get_columns(table_name, schema=schema_name)

                return [
                    ColumnInfo(
                        name=col["name"],
                        type=str(col["type"]),
                        nullable=col.get("nullable", True),
                        default=str(col.get("default")) if col.get("default") is not None else None,
                        comment=col.get("comment"),
                    )
                    for col in columns
                ]

        except Exception as e:
            logger.error(f"Failed to get columns for {source_name}.{table_name}: {str(e)}")
            return []

    async def execute_query(self, db: Session, source_name: str, query: str) -> Optional[DataSourceQueryResult]:
        """Execute a SQL query and return results"""
        # Get source info to determine database type
        data_source = await get_data_source(db, source_name)
        if not data_source:
            return None

        kind = DatabaseKind(data_source.kind)

        # Kafka doesn't support SQL queries
        if kind == DatabaseKind.KAFKA:
            raise Exception("SQL queries are not supported for Kafka data sources. Use Kafka-specific operations instead.")

        engine = await self.get_engine(db, source_name)
        if not engine:
            return None

        try:
            start_time = time.time()

            with engine.connect() as conn:
                result = conn.execute(text(query))

                # Get column names
                columns = list(result.keys()) if result.keys() else []

                # Fetch rows
                rows = []
                for row in result:
                    # Convert row to list, handling special types
                    row_data = []
                    for value in row:
                        if value is None:
                            row_data.append(None)
                        else:
                            row_data.append(str(value))
                    rows.append(row_data)

                execution_time_ms = (time.time() - start_time) * 1000

                return DataSourceQueryResult(columns=columns, rows=rows, row_count=len(rows), execution_time_ms=round(execution_time_ms, 2))

        except Exception as e:
            logger.error(f"Failed to execute query on {source_name}: {str(e)}")
            raise Exception(f"Query execution failed: {str(e)}")

    def close_engine(self, source_name: str):
        """Close and remove an engine"""
        if source_name in self._engines:
            self._engines[source_name].dispose()
            del self._engines[source_name]
            logger.info(f"Closed database engine for source: {source_name}")

    def close_all_engines(self):
        """Close all engines"""
        for source_name in list(self._engines.keys()):
            self.close_engine(source_name)

    async def test_connection(
        self,
        kind: DatabaseKind,
        host: Optional[str],
        port: Optional[int],
        database: str,
        user: Optional[str],
        password: Optional[str],
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> DataSourceConnectionTestResult:
        """Test database connection without persisting credentials"""
        start_time = time.time()

        try:
            # Handle Kafka connection test differently
            if kind == DatabaseKind.KAFKA:
                # For Kafka, validate that bootstrap.servers is provided
                if not extra_params or not extra_params.get("bootstrap.servers"):
                    return DataSourceConnectionTestResult(
                        success=False,
                        message="Connection test failed: Kafka data sources require 'bootstrap.servers' in extra_params",
                        connection_time_ms=round((time.time() - start_time) * 1000, 2),
                    )

                # Test actual Kafka connection using aiokafka
                bootstrap_servers = extra_params.get("bootstrap.servers")

                try:
                    # Parse bootstrap servers - can be comma-separated
                    if isinstance(bootstrap_servers, str):
                        servers = [server.strip() for server in bootstrap_servers.split(",")]
                    else:
                        servers = bootstrap_servers

                    # Create a producer to test the connection
                    producer = AIOKafkaProducer(
                        bootstrap_servers=servers,
                        client_id="resinkit_connection_test",
                        request_timeout_ms=5000,  # 5 second timeout
                        retry_backoff_ms=100,
                    )

                    # Start the producer to establish connection
                    await producer.start()

                    # If we get here, connection was successful
                    await producer.stop()

                    connection_time_ms = (time.time() - start_time) * 1000

                    return DataSourceConnectionTestResult(
                        success=True,
                        message=f"Successfully connected to Kafka cluster at: {bootstrap_servers}",
                        connection_time_ms=round(connection_time_ms, 2),
                    )

                except Exception as kafka_error:
                    connection_time_ms = (time.time() - start_time) * 1000
                    error_message = f"Failed to connect to Kafka cluster at {bootstrap_servers}: {str(kafka_error)}"
                    logger.error(error_message)

                    return DataSourceConnectionTestResult(
                        success=False,
                        message=error_message,
                        connection_time_ms=round(connection_time_ms, 2),
                    )

            # Handle SQL database connections
            # Build connection URL
            connection_url = self._get_connection_url(
                source_name="test_connection",  # Temporary name for testing
                kind=kind,
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                extra_params=extra_params or {},
            )

            # Create temporary engine for testing
            engine = create_engine(connection_url, echo=False)

            # Test connection with a simple query
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            # Clean up the temporary engine
            engine.dispose()

            connection_time_ms = (time.time() - start_time) * 1000

            return DataSourceConnectionTestResult(success=True, message="Connection test successful", connection_time_ms=round(connection_time_ms, 2))

        except Exception as e:
            connection_time_ms = (time.time() - start_time) * 1000
            error_message = f"Connection test failed: {str(e)}"
            logger.error(error_message)

            return DataSourceConnectionTestResult(success=False, message=error_message, connection_time_ms=round(connection_time_ms, 2))


# Global connection manager instance
connection_manager = SqlConnectionManager()
