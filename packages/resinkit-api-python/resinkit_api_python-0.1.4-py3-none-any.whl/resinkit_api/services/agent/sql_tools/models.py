from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DatabaseKind(str, Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    ORACLE = "oracle"
    MSSQL = "mssql"
    SQLITE = "sqlite"
    KAFKA = "kafka"


class DataSourceCreate(BaseModel):
    name: str = Field(..., description="Unique name for the SQL source")
    kind: DatabaseKind = Field(..., description="Type of database")
    host: Optional[str] = Field(None, description="Database host (not required for sqlite)")
    port: Optional[int] = Field(None, description="Database port (not required for sqlite)")
    database: Optional[str] = Field(None, description="Database name")
    user: Optional[str] = Field(None, description="Username (not required for sqlite, can reference variables)")
    password: Optional[str] = Field(None, description="Password (not required for sqlite, can reference variables)")
    query_timeout: Optional[str] = Field("30s", description="Query timeout duration")
    extra_params: Optional[Dict[str, Any]] = Field(None, description="Additional connection parameters")


class DataSourceUpdate(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    query_timeout: Optional[str] = None
    extra_params: Optional[Dict[str, Any]] = None


class DataSourceResponse(BaseModel):
    name: str
    kind: DatabaseKind
    host: Optional[str] = None
    port: Optional[int] = None
    database: str
    user: Optional[str] = None
    query_timeout: str
    extra_params: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str
    created_by: str

    class Config:
        # Exclude None values from the response
        exclude_none = True


class DatabaseInfo(BaseModel):
    name: str


class SchemaInfo(BaseModel):
    name: str


class TableInfo(BaseModel):
    name: str
    schema_name: Optional[str] = None
    type: Optional[str] = None


class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool
    default: Optional[str] = None
    comment: Optional[str] = None


class DataSourceQueryRequest(BaseModel):
    source_name: str = Field(..., description="Name of the SQL source to execute against")
    query: str = Field(..., description="SQL query to execute")
    limit: Optional[int] = Field(1000, description="Maximum number of rows to return")


class DataSourceQueryResult(BaseModel):
    columns: List[str]
    rows: List[List[Any]]
    row_count: int
    execution_time_ms: float


class DataSourceConnectionTestResult(BaseModel):
    success: bool = Field(..., description="Whether the connection test succeeded")
    message: str = Field(..., description="Success or error message")
    connection_time_ms: Optional[float] = Field(None, description="Connection time in milliseconds")
