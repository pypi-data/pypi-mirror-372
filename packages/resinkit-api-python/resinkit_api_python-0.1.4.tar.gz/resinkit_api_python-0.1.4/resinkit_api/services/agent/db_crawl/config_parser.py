import hashlib
import re
from typing import List, Union

from resinkit_api.core.logging import get_logger
from resinkit_api.services.agent.db_crawl.models import (
    DbCrawlConfig,
    TableRegexSelection,
    TableSelection,
)

logger = get_logger(__name__)


class ConfigParser:
    """Parser for database crawl configuration"""

    def __init__(self, config: DbCrawlConfig):
        self.config = config
        self._config_hash = self._calculate_config_hash()

    def _calculate_config_hash(self) -> str:
        """Calculate a hash of the configuration for tracking purposes"""
        config_dict = self.config.model_dump()
        # Sort keys manually for consistent hashing
        config_str = str(sorted(config_dict.items()))
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]

    def get_config_hash(self) -> str:
        """Get the configuration hash"""
        return self._config_hash

    def get_source_name(self) -> str:
        """Get the SQL source name"""
        return self.config.source

    def get_default_sample_rows(self) -> int:
        """Get the default number of sample rows"""
        return self.config.defaults.sample_rows

    def get_table_specifications(self) -> List[Union[TableSelection, TableRegexSelection]]:
        """Get all table specifications"""
        if self.config.tables is None:
            # If no tables specified, return a regex selection that matches all tables
            return [TableRegexSelection(name_regex=".*")]
        return self.config.tables

    def get_dsds_config(self):
        """Get DSDS configuration"""
        return self.config.dsds

    def validate_regex_patterns(self) -> List[str]:
        """Validate regex patterns in table specifications"""
        errors = []

        # Get table specifications (which handles None case)
        table_specs = self.get_table_specifications()

        for table_spec in table_specs:
            if isinstance(table_spec, TableRegexSelection):
                try:
                    re.compile(table_spec.name_regex)
                except re.error as e:
                    errors.append(f"Invalid regex pattern '{table_spec.name_regex}': {str(e)}")

        return errors

    def resolve_table_selection(self, available_tables: List[str]) -> List[tuple[str, Union[TableSelection, TableRegexSelection]]]:
        """
        Resolve table specifications against available tables.
        Returns list of (table_name, original_spec) tuples.
        """
        resolved_tables = []

        # Get table specifications (which handles None case)
        table_specs = self.get_table_specifications()

        for table_spec in table_specs:
            if isinstance(table_spec, TableSelection):
                # Direct table name match
                if table_spec.name in available_tables:
                    resolved_tables.append((table_spec.name, table_spec))
                else:
                    logger.warning(f"Table '{table_spec.name}' not found in available tables")

            elif isinstance(table_spec, TableRegexSelection):
                # Regex pattern matching
                try:
                    pattern = re.compile(table_spec.name_regex)
                    matched_tables = [table for table in available_tables if pattern.match(table)]

                    if matched_tables:
                        for table_name in matched_tables:
                            resolved_tables.append((table_name, table_spec))
                    else:
                        logger.warning(f"No tables matched regex pattern '{table_spec.name_regex}'")

                except re.error as e:
                    logger.error(f"Invalid regex pattern '{table_spec.name_regex}': {str(e)}")

        return resolved_tables

    def get_effective_sample_rows(self, table_spec: Union[TableSelection, TableRegexSelection]) -> int:
        """Get effective sample rows for a table specification"""
        if table_spec.sample_rows is not None:
            return table_spec.sample_rows
        return self.get_default_sample_rows()

    def get_effective_columns(self, table_spec: Union[TableSelection, TableRegexSelection]) -> List[str]:
        """Get effective columns for a table specification (None means all columns)"""
        return table_spec.columns

    def get_custom_sample_query(self, table_spec: Union[TableSelection, TableRegexSelection]) -> str:
        """Get custom sample query for a table specification"""
        return table_spec.sample_query

    def should_generate_dsds(self) -> bool:
        """Check if DSDS should be generated"""
        return self.config.dsds.generate
