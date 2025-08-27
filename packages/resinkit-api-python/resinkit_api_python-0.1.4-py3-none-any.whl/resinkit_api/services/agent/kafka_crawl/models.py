from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ValueDeserializer(str, Enum):
    """Supported message value deserializers"""

    JSON = "json"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    STRING = "string"


class SamplingStrategy(str, Enum):
    """Message sampling strategies"""

    LATEST = "latest"
    EARLIEST = "earliest"
    LATEST_OFFSET = "latest_offset"


class KafkaSource(BaseModel):
    """Kafka cluster connection configuration"""

    bootstrap_servers: str = Field(..., description="Comma-separated list of Kafka brokers")
    security_protocol: Optional[str] = Field(None, description="Security protocol (e.g., SASL_SSL)")
    sasl_mechanism: Optional[str] = Field(None, description="SASL mechanism (e.g., PLAIN)")
    schema_registry_url: Optional[str] = Field(None, description="Schema Registry URL for Avro/Protobuf")
    # Additional optional fields for authentication
    sasl_username: Optional[str] = Field(None, description="SASL username")
    sasl_password: Optional[str] = Field(None, description="SASL password")


class DefaultSettings(BaseModel):
    """Global default settings for message sampling"""

    sample_messages: int = Field(2, description="Default number of messages to sample")
    sampling_strategy: SamplingStrategy = Field(SamplingStrategy.EARLIEST, description="Default sampling strategy")
    consumer_timeout_ms: int = Field(5000, description="Consumer timeout in milliseconds")


class TopicSelection(BaseModel):
    """Configuration for selecting a specific topic"""

    name: str = Field(..., description="Topic name")
    value_deserializer: ValueDeserializer = Field(ValueDeserializer.JSON, description="Message value deserializer")
    sample_messages: Optional[int] = Field(None, description="Override default sample message count")
    sampling_strategy: Optional[SamplingStrategy] = Field(None, description="Override default sampling strategy")
    fields: Optional[List[str]] = Field(None, description="Specific fields to analyze (default: all)")


class TopicRegexSelection(BaseModel):
    """Configuration for selecting topics using regex"""

    name_regex: str = Field(..., description="Regular expression to match topic names")
    value_deserializer: ValueDeserializer = Field(ValueDeserializer.JSON, description="Message value deserializer")
    sample_messages: Optional[int] = Field(None, description="Override default sample message count")
    sampling_strategy: Optional[SamplingStrategy] = Field(None, description="Override default sampling strategy")
    fields: Optional[List[str]] = Field(None, description="Specific fields to analyze (default: all)")


class AnalysisConfig(BaseModel):
    """Configuration for statistical analysis"""

    calculate_null_percentage: bool = Field(True, description="Calculate null percentage for fields")
    estimate_cardinality: bool = Field(True, description="Estimate cardinality of field values")


class SchemaInferenceConfig(BaseModel):
    """Configuration for schema inference"""

    generate: bool = Field(True, description="Whether to generate inferred schemas")
    include_examples: bool = Field(True, description="Include example values in field analysis")
    max_examples_per_field: int = Field(3, description="Maximum number of examples per field")
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)


class KafkaCrawlConfig(BaseModel):
    """Main configuration for Kafka message crawling"""

    kafka_source: KafkaSource = Field(..., description="Kafka cluster connection details")
    defaults: DefaultSettings = Field(default_factory=DefaultSettings)
    topics: List[Union[TopicSelection, TopicRegexSelection]] = Field(..., min_length=1, description="List of topic specifications")
    schema_inference: SchemaInferenceConfig = Field(default_factory=SchemaInferenceConfig)


class KafkaRetrievalMetadata(BaseModel):
    """Metadata about the Kafka crawl operation"""

    timestamp_utc: str = Field(..., description="UTC timestamp when crawl was performed")
    kafka_source: str = Field(..., description="Kafka bootstrap servers")
    config_hash: str = Field(..., description="Hash of the configuration used")


class KafkaJsonSchemaProperty(BaseModel):
    """JSON Schema property definition for Kafka messages"""

    type: str = Field(..., description="Property type")
    format: Optional[str] = Field(None, description="Property format")
    items: Optional[Dict[str, Any]] = Field(None, description="Array items schema")
    properties: Optional[Dict[str, Any]] = Field(None, description="Object properties schema")
    required: Optional[List[str]] = Field(None, description="Required properties for objects")


class KafkaInferredSchema(BaseModel):
    """Inferred JSON schema for a Kafka topic"""

    type: str = Field(..., description="Root schema type")
    properties: Optional[Dict[str, KafkaJsonSchemaProperty]] = Field(None, description="Schema properties")
    required: Optional[List[str]] = Field(None, description="Required properties")


class KafkaFieldAnalysis(BaseModel):
    """Analysis results for a specific Kafka message field"""

    inferred_type: str = Field(..., description="Inferred data type")
    examples: List[Any] = Field(..., description="Example values")
    analysis: Dict[str, Any] = Field(..., description="Statistical analysis results")


class KafkaTopicCrawlResult(BaseModel):
    """Result of crawling a single Kafka topic"""

    topic_name: str = Field(..., description="Name of the topic")
    partitions: int = Field(..., description="Number of partitions")
    inferred_schema: Optional[KafkaInferredSchema] = Field(None, description="Inferred JSON schema")
    sample_messages: List[Any] = Field(..., description="Sample messages from the topic")
    field_analysis: Optional[Dict[str, KafkaFieldAnalysis]] = Field(None, description="Field-level analysis")


class KafkaCrawlResult(BaseModel):
    """Complete result of Kafka crawling operation"""

    retrieval_metadata: KafkaRetrievalMetadata = Field(..., description="Metadata about the crawl operation")
    topics: List[KafkaTopicCrawlResult] = Field(..., description="Results for each crawled topic")


class KafkaCrawlRequest(BaseModel):
    """Request model for Kafka crawl API"""

    config: KafkaCrawlConfig = Field(..., description="Kafka crawl configuration")
