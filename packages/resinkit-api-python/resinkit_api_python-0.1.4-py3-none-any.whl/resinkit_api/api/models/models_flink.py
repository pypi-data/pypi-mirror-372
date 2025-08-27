from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class SQLQuery(BaseModel):
    sql: str


class OpenSessionRequest(BaseModel):
    properties: Optional[Dict[str, str]] = None
    session_name: Optional[str] = None


class OpenSessionResponse(BaseModel):
    session_id: str


class ExecuteSQLRequest(BaseModel):
    sql: str
    execution_config: Optional[Dict[str, Any]] = None
    execution_timeout: Optional[int] = None


class ColumnDefinition(BaseModel):
    name: str
    logical_type: Dict[str, Any]
    comment: Optional[str] = None


class FetchResultData(BaseModel):
    columns: List[ColumnDefinition]
    data: List[List[Any]]
    eos: bool
    job_id: Optional[str] = None
    is_query_result: Optional[bool] = None


class SQLExecutionMetadata(BaseModel):
    sql: str
    session_id: str
    operation_id: str


class StreamingSQLResponse(BaseModel):
    meta_data: SQLExecutionMetadata
    fetch_result: FetchResultData


class HeartbeatResponse(BaseModel):
    success: bool
    message: Optional[str] = None


class CloseSessionResponse(BaseModel):
    success: bool
    message: Optional[str] = None
