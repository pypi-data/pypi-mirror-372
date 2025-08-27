import re
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from resinkit_api.core.logging import get_logger
from resinkit_api.services.agent.db_crawl.config_parser import ConfigParser
from resinkit_api.services.agent.db_crawl.models import ColumnDSDS
from resinkit_api.services.agent.sql_tools.connection_manager import connection_manager

logger = get_logger(__name__)


class DSDSGenerator:
    """Generates Descriptive Sample Data Schema (DSDS) for tables"""

    def __init__(self, config_parser: ConfigParser):
        self.config_parser = config_parser
        self.dsds_config = config_parser.get_dsds_config()

    def _extract_column_attributes(self, ddl: str, column_name: str) -> List[str]:
        """Extract attributes for a column from DDL"""
        attributes = []

        if not self.dsds_config.attribute_detection:
            return attributes

        # Convert DDL to uppercase for easier matching
        ddl_upper = ddl.upper()
        column_upper = column_name.upper()

        # Look for column definition line
        column_pattern = rf"\b{re.escape(column_upper)}\b.*"
        column_match = re.search(column_pattern, ddl_upper, re.MULTILINE)

        if not column_match:
            return attributes

        column_line = column_match.group(0)

        # Check for various attributes
        if self.dsds_config.attribute_detection.primary_key:
            if "PRIMARY KEY" in column_line or "PRIMARY KEY" in ddl_upper:
                attributes.append("PRIMARY KEY")

        if self.dsds_config.attribute_detection.not_null:
            if "NOT NULL" in column_line:
                attributes.append("NOT NULL")

        if self.dsds_config.attribute_detection.unique_constraint:
            if "UNIQUE" in column_line:
                attributes.append("UNIQUE")

        if self.dsds_config.attribute_detection.default_value:
            if "DEFAULT" in column_line:
                # Extract default value
                default_match = re.search(r"DEFAULT\s+([^,\s)]+)", column_line)
                if default_match:
                    attributes.append(f"DEFAULT {default_match.group(1)}")

        if self.dsds_config.attribute_detection.foreign_key:
            # Look for foreign key references (simplified)
            if "REFERENCES" in column_line or f"FOREIGN KEY.*{re.escape(column_upper)}" in ddl_upper:
                # Try to extract the referenced table
                ref_match = re.search(r"REFERENCES\s+(\w+)", column_line)
                if ref_match:
                    attributes.append(f"FOREIGN KEY REFERENCES {ref_match.group(1)}")
                else:
                    attributes.append("FOREIGN KEY")

        return attributes

    def _infer_column_type(self, ddl_type: str, examples: List[Any]) -> str:
        """Infer and potentially refine column type based on examples"""
        if not self.dsds_config.type_inference.enable:
            return ddl_type

        # Start with DDL type
        inferred_type = ddl_type

        # Type inference based on sample data
        if examples and self.dsds_config.type_inference.string_length_threshold:
            for example in examples:
                if isinstance(example, str) and len(example) > self.dsds_config.type_inference.string_length_threshold:
                    # If we find long strings, classify as 'text' type
                    if "varchar" in ddl_type.lower() or "char" in ddl_type.lower():
                        inferred_type = "text"
                        break

        return inferred_type

    def _generate_column_comment(self, column_name: str, column_type: str, examples: List[Any]) -> Optional[str]:  # noqa: ARG002
        """Generate a descriptive comment for a column"""
        if not self.dsds_config.include_comments:
            return None

        # No need to generate comment at the moment yet
        return None

    async def generate_table_dsds(self, db: Session, table_info: Dict[str, Any]) -> Dict[str, ColumnDSDS]:
        """Generate DSDS for a single table"""
        if not self.dsds_config.generate:
            return {}

        source_name = self.config_parser.get_source_name()
        table_name = table_info["table_name"]
        schema_name = table_info.get("schema_name")
        ddl = table_info["ddl"]
        sample_data = table_info["sample_data"]

        logger.info(f"Generating DSDS for table {table_name}")

        try:
            # Get column information from the database
            columns = await connection_manager.get_table_columns(db, source_name, table_name, schema_name)

            dsds = {}

            for column in columns:
                column_name = column.name
                ddl_type = column.type

                # Extract examples from sample data
                examples = []
                if self.dsds_config.include_examples and sample_data:
                    for row in sample_data:
                        if column_name in row and row[column_name] is not None:
                            examples.append(row[column_name])

                    # Limit number of examples
                    max_examples = self.dsds_config.max_examples_per_column
                    if len(examples) > max_examples:
                        examples = examples[:max_examples]

                # Infer type
                inferred_type = self._infer_column_type(str(ddl_type), examples)

                # Extract attributes
                attributes = self._extract_column_attributes(ddl, column_name)

                # Use database comment if available, otherwise generate one
                comment = column.comment
                if not comment:
                    comment = self._generate_column_comment(column_name, inferred_type, examples)

                # Create DSDS entry
                dsds[column_name] = ColumnDSDS(type=inferred_type, examples=examples, attributes=attributes, comment=comment)

            logger.info(f"Generated DSDS for {len(dsds)} columns in table {table_name}")
            return dsds

        except Exception as e:
            logger.error(f"Failed to generate DSDS for table {table_name}: {str(e)}")
            return {}

    async def generate_dsds_for_tables(self, db: Session, crawled_tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate DSDS for all crawled tables"""
        if not self.dsds_config.generate:
            logger.info("DSDS generation is disabled")
            return crawled_tables

        logger.info(f"Generating DSDS for {len(crawled_tables)} tables")

        enriched_tables = []
        for table_info in crawled_tables:
            try:
                # Generate DSDS for this table
                dsds = await self.generate_table_dsds(db, table_info)

                # Add DSDS to table info
                enriched_table = table_info.copy()
                enriched_table["dsds"] = self.dsds_to_string(dsds, table_info["table_name"])
                enriched_tables.append(enriched_table)

            except Exception as e:
                logger.error(f"Failed to generate DSDS for table {table_info.get('table_name', 'unknown')}: {str(e)}")
                # Include table without DSDS
                enriched_table = table_info.copy()
                enriched_table["dsds"] = f"table: {table_info.get('table_name', 'unknown')}"
                enriched_tables.append(enriched_table)

        logger.info(f"DSDS generation completed for {len(enriched_tables)} tables")
        return enriched_tables

    @staticmethod
    def dsds_to_string(dsds: Dict[str, ColumnDSDS], table_name: str) -> str:
        """Convert Dict[str, ColumnDSDS] to formatted string representation"""
        if not dsds:
            return f"table: {table_name}\n"

        lines = [f"table: {table_name}"]

        for column_name, column_dsds in dsds.items():
            # Format examples
            examples_str = ""
            if column_dsds.examples:
                examples_list = ", ".join(str(ex) for ex in column_dsds.examples)
                examples_str = f", Examples: [{examples_list}]"

            # Format comment
            comment_str = ""
            if column_dsds.comment:
                comment_str = f', Comment: "{column_dsds.comment}"'

            # Build column line
            column_line = f"<column> {column_name}:{column_dsds.type}{comment_str}{examples_str} </column>"
            lines.append(column_line)

        return "\n".join(lines)
