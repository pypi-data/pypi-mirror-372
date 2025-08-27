from typing import Any, AsyncGenerator, Dict, List, Optional

from flink_gateway_api.api.default import close_operation, execute_statement
from flink_gateway_api.models import ExecuteStatementRequestBody
from sqlalchemy.orm import Session

from resinkit_api.api.models.models_flink import (
    ColumnDefinition,
    FetchResultData,
    SQLExecutionMetadata,
    StreamingSQLResponse,
)
from resinkit_api.clients.sql_gateway.flink_utils import compact_flink_sql_error_message
from resinkit_api.clients.sql_gateway.session_utils import (
    FetchResultData as ClientFetchResultData,
)
from resinkit_api.clients.sql_gateway.session_utils import (
    fetch_results_async_gen,
    get_execute_statement_request,
)
from resinkit_api.core.logging import get_logger
from resinkit_api.db.variables_crud import get_all_variables_decrypted
from resinkit_api.services.flink_session_service import FlinkSessionService
from resinkit_api.utils.misc_utils import render_with_string_template

logger = get_logger(__name__)


class FlinkSQLExecutionService:
    """Service for executing Flink SQL statements with streaming results."""

    def __init__(self, session_service: FlinkSessionService):
        self.session_service = session_service

    @staticmethod
    async def parse_sql_statements(sql_text: str, db: Optional[Session] = None) -> List[str]:
        """
        Parse SQL text into individual statements with variable substitution.

        Args:
            sql_text: The SQL text containing multiple statements
            db: Database session for variable resolution

        Returns:
            List of individual SQL statements with variables resolved
        """
        if not sql_text:
            return []

        # Apply variable substitution if database session is provided
        if db:
            variables = await get_all_variables_decrypted(db)
            sql_text = render_with_string_template(sql_text, variables)

        statements = []
        current_statement = []
        in_string = False
        string_char = None

        for line in sql_text.splitlines():
            line = line.strip()
            if not line or line.startswith("--"):  # Skip empty lines and comments
                continue

            i = 0
            while i < len(line):
                char = line[i]

                if not in_string and char in ("'", '"'):
                    in_string = True
                    string_char = char
                elif in_string and char == string_char:
                    # Check for escaped quotes
                    if i + 1 < len(line) and line[i + 1] == string_char:
                        i += 1  # Skip the escaped quote
                    else:
                        in_string = False
                        string_char = None
                elif not in_string and char == ";":
                    # End of statement
                    current_statement.append(line[:i])
                    stmt = " ".join(current_statement).strip()
                    if stmt:
                        statements.append(stmt)
                    current_statement = []
                    line = line[i + 1 :].strip()
                    i = -1  # Reset index for remaining line
                i += 1

            # Add remaining part of line to current statement
            if line:
                current_statement.append(line)

        # Add the last statement if exists
        if current_statement:
            stmt = " ".join(current_statement).strip()
            if stmt:
                statements.append(stmt)

        return statements

    def convert_fetch_result_data(self, client_result: ClientFetchResultData, sql: str, session_id: str, operation_id: str) -> StreamingSQLResponse:
        """
        Convert client FetchResultData to API response format.

        Args:
            client_result: Result from the Flink client
            sql: The SQL statement executed
            session_id: Session ID
            operation_id: Operation ID

        Returns:
            StreamingSQLResponse for API
        """
        # Convert columns
        columns = []
        for col in client_result.columns:
            columns.append(ColumnDefinition(name=col["name"], logical_type=col["logicalType"], comment=col.get("comment")))

        # Create metadata
        metadata = SQLExecutionMetadata(sql=sql, session_id=session_id, operation_id=operation_id)

        # Create fetch result
        fetch_result = FetchResultData(
            columns=columns, data=client_result.data, eos=client_result.eos, job_id=client_result.job_id, is_query_result=client_result.is_query_result
        )

        return StreamingSQLResponse(meta_data=metadata, fetch_result=fetch_result)

    async def execute_sql_streaming(
        self,
        session_id: str,
        sql: str,
        execution_config: Optional[Dict[str, Any]] = None,
        execution_timeout: Optional[int] = None,
        poll_interval_secs: float = 0.1,
        max_poll_secs: Optional[float] = None,
        n_row_limit: Optional[int] = None,
        db: Optional[Session] = None,
    ) -> AsyncGenerator[StreamingSQLResponse, None]:
        """
        Execute SQL statements and stream results.

        Args:
            session_id: Session ID
            sql: SQL text (may contain multiple statements)
            execution_config: Execution configuration
            execution_timeout: Execution timeout
            poll_interval_secs: Polling interval for results
            max_poll_secs: Maximum polling time
            n_row_limit: Maximum number of rows to fetch
            db: Database session for variable resolution

        Yields:
            StreamingSQLResponse objects
        """
        session_info = self.session_service.get_session(session_id)
        if not session_info:
            raise ValueError(f"Session {session_id} not found")

        # Parse SQL into individual statements
        statements = await self.parse_sql_statements(sql, db)
        if not statements:
            raise ValueError("No valid SQL statements found")

        logger.info(f"Executing {len(statements)} SQL statements in session {session_id}")

        # Execute each statement
        for i, statement in enumerate(statements):
            logger.info(f"Executing statement {i+1}/{len(statements)}: {statement[:100]}...")

            operation_handle = None
            try:
                # Execute statement using flink_gateway_api directly
                request_dict = get_execute_statement_request(statement, execution_config, execution_timeout)
                response = await execute_statement.asyncio(
                    session_info.session_handle, client=session_info.client, body=ExecuteStatementRequestBody.from_dict(request_dict)
                )

                operation_handle = response.operation_handle
                logger.debug(f"Started operation {operation_handle} for statement {i+1}")

                # Stream results from this operation
                async for client_result in fetch_results_async_gen(
                    client=session_info.client,
                    session_handle=session_info.session_handle,
                    operation_handle=operation_handle,
                    poll_interval_secs=poll_interval_secs,
                    max_poll_secs=max_poll_secs,
                    n_row_limit=n_row_limit,
                ):
                    # Convert to API response format
                    api_response = self.convert_fetch_result_data(client_result, statement, session_id, operation_handle)
                    yield api_response

                    # If this is the end of stream for this operation, break
                    if client_result.eos:
                        break

                # Close the operation
                if operation_handle:
                    try:
                        await close_operation.asyncio(session_info.session_handle, operation_handle, client=session_info.client)
                    except Exception as close_e:
                        logger.warning(f"Failed to close operation {operation_handle}: {close_e}")

            except Exception as e:
                logger.error(f"Error executing statement {i+1}: {str(e)}")

                # Try to close operation if it was created
                if operation_handle:
                    try:
                        await close_operation.asyncio(session_info.session_handle, operation_handle, client=session_info.client)
                    except Exception:
                        pass  # Ignore errors when cleaning up

                # bubble up the error
                raise RuntimeError(compact_flink_sql_error_message(e))
