from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class TableSelection(BaseModel):
    """Configuration for selecting a specific table"""

    name: str = Field(..., description="Table name (fully qualified preferred)")
    columns: Optional[List[str]] = Field(None, description="Specific columns to include (default: all)")
    sample_rows: Optional[int] = Field(None, description="Override default sample rows for this table")
    sample_query: Optional[str] = Field(None, description="Custom SQL query to fetch sample data")


class TableRegexSelection(BaseModel):
    """Configuration for selecting tables using regex"""

    name_regex: str = Field(..., description="Regular expression to match table names")
    columns: Optional[List[str]] = Field(None, description="Specific columns to include (default: all)")
    sample_rows: Optional[int] = Field(None, description="Override default sample rows for this table")
    sample_query: Optional[str] = Field(None, description="Custom SQL query to fetch sample data")


class GlobalDefaults(BaseModel):
    """Global default settings"""

    sample_rows: int = Field(3, description="Default number of sample rows to retrieve")


class TypeInferenceConfig(BaseModel):
    """Configuration for custom column type inference"""

    enable: bool = Field(True, description="Enable custom type inference")
    string_length_threshold: int = Field(50, description="Strings longer than this are classified as 'text'")


class AttributeDetectionConfig(BaseModel):
    """Configuration for attribute detection"""

    primary_key: bool = Field(True, description="Detect primary key attributes")
    foreign_key: bool = Field(True, description="Detect foreign key attributes")
    unique_constraint: bool = Field(True, description="Detect unique constraint attributes")
    not_null: bool = Field(True, description="Detect not null attributes")
    default_value: bool = Field(True, description="Detect default value attributes")


class DSDSConfig(BaseModel):
    """Configuration for Descriptive Sample Data Schema generation"""

    generate: bool = Field(True, description="Whether to generate DSDS")
    include_examples: bool = Field(True, description="Include example values in DSDS")
    max_examples_per_column: int = Field(3, description="Maximum number of examples per column")
    include_comments: bool = Field(True, description="Include column comments if available")
    type_inference: TypeInferenceConfig = Field(default_factory=TypeInferenceConfig)
    attribute_detection: AttributeDetectionConfig = Field(default_factory=AttributeDetectionConfig)


class DbCrawlConfig(BaseModel):
    """Main configuration for database crawling"""

    source: str = Field(..., description="SQL source name (configured via /sources endpoints)")
    defaults: GlobalDefaults = Field(default_factory=GlobalDefaults)
    tables: Optional[List[Union[TableSelection, TableRegexSelection]]] = Field(
        None, description="List of table specifications (if not provided, crawls all tables)"
    )
    dsds: DSDSConfig = Field(default_factory=DSDSConfig)


class RetrievalMetadata(BaseModel):
    """Metadata about the crawl operation"""

    timestamp_utc: str = Field(..., description="UTC timestamp when crawl was performed")
    source_database: str = Field(..., description="Source database name")
    config_hash: str = Field(..., description="Hash of the configuration used")


class ColumnDSDS(BaseModel):
    """Descriptive Sample Data Schema for a column"""

    type: str = Field(..., description="Column data type")
    examples: List[Any] = Field(..., description="Example values from the column")
    attributes: List[str] = Field(..., description="Column attributes (PRIMARY KEY, NOT NULL, etc.)")
    comment: Optional[str] = Field(None, description="Column comment if available")


class TableCrawlResult(BaseModel):
    """Result of crawling a single table"""

    table_name: str = Field(..., description="Name of the table")
    full_path: str = Field(..., description="Full path including schema if applicable")
    ddl: str = Field(..., description="DDL (CREATE TABLE statement) for the table")
    sample_data: List[Dict[str, Any]] = Field(..., description="Sample data from the table")
    dsds: Optional[str] = Field(None, description="Descriptive Sample Data Schema as formatted string")


class DbCrawlResult(BaseModel):
    """Complete result of database crawling operation"""

    retrieval_metadata: RetrievalMetadata = Field(..., description="Metadata about the crawl operation")
    tables: List[TableCrawlResult] = Field(..., description="Results for each crawled table")


class DbCrawlRequest(BaseModel):
    """Request model for database crawl API"""

    config: DbCrawlConfig = Field(..., description="Database crawl configuration")
    save_remote: bool = Field(True, description="Save crawled results to remote file system")
