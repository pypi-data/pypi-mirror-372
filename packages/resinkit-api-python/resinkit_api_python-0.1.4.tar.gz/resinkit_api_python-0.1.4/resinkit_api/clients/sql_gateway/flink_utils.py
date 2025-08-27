"""
Utility functions and classes for Flink SQL Gateway operations.
These utilities can be reused without the deprecated wrapper classes.
"""

from dataclasses import dataclass

CAUSED_BY_PATTERN = r"Caused by: (.+?)(?=\\n\\t)"


class FlinkSqlGatewayNotFoundException(Exception):
    """Base exception for Flink SQL Gateway not found errors."""

    pass


class FlinkSqlGatewayOperationNotFoundError(FlinkSqlGatewayNotFoundException):
    """Exception raised when a Flink operation is not found."""

    pass


class FlinkSqlGatewaySessionNotFoundError(FlinkSqlGatewayNotFoundException):
    """Exception raised when a Flink session is not found."""

    pass


def maybe_not_found_exception(exception: Exception) -> FlinkSqlGatewayNotFoundException | None:
    """Get the Flink operation exception type from an exception."""
    if hasattr(exception, "content"):
        content = exception.content.decode("utf-8")
        if "Can not find the submitted operation" in content:
            return FlinkSqlGatewayOperationNotFoundError(exception)
        elif "org.apache.flink.table.gateway.service.session.SessionManagerImpl.getSession" in content and "does not exist" in content:
            return FlinkSqlGatewaySessionNotFoundError(exception)
    return None


@dataclass
class ResultsFetchOpts:
    """Options for fetching results from Flink operations."""

    poll_interval_secs: float = 0.1
    max_poll_secs: float = 10  # set to 0 or negative to pull once
    n_row_limit: int = 500

    def __post_init__(self):
        if self.poll_interval_secs < 0:
            raise ValueError(f"poll_interval_secs must be non-negative, got {self.poll_interval_secs}")

        if self.n_row_limit < 0:
            raise ValueError(f"n_row_limit must be non-negative, got {self.n_row_limit}")


# Predefined options for pulling results once
PULL_ONCE_OPTS = ResultsFetchOpts(max_poll_secs=0)


def compact_flink_sql_error_message(err: Exception) -> str:
    """
    Extract all "Caused by" lines from Flink SQL Gateway exceptions.

    Args:
        err: Exception caught from Flink SQL Gateway operations

    Returns:
        All "Caused by" lines, one per line
    """
    import re

    error_text = str(err)

    # Find all "Caused by" lines (just the first line, not the stack trace)
    matches = re.findall(CAUSED_BY_PATTERN, error_text)

    if not matches:
        return error_text

    return "\\n".join(matches)


__all__ = [
    "FlinkSqlGatewayNotFoundException",
    "FlinkSqlGatewayOperationNotFoundError",
    "FlinkSqlGatewaySessionNotFoundError",
    "maybe_not_found_exception",
    "ResultsFetchOpts",
    "PULL_ONCE_OPTS",
    "compact_flink_sql_error_message",
]
