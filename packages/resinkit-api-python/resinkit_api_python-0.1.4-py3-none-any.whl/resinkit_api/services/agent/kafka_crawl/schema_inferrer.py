import json
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Union

from resinkit_api.core.logging import get_logger
from resinkit_api.services.agent.kafka_crawl.config_parser import KafkaConfigParser
from resinkit_api.services.agent.kafka_crawl.models import (
    KafkaFieldAnalysis,
    KafkaInferredSchema,
    KafkaJsonSchemaProperty,
)

logger = get_logger(__name__)


class SchemaInferrer:
    """Infers JSON schemas and analyzes fields from Kafka message samples"""

    def __init__(self, config_parser: KafkaConfigParser):
        self.config_parser = config_parser
        self.schema_config = config_parser.get_schema_inference_config()

    def _infer_type_from_value(self, value: Any) -> str:
        """Infer JSON Schema type from a Python value"""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "string"

    def _get_nested_paths(self, obj: Any, prefix: str = "") -> Dict[str, List[Any]]:
        """Extract all nested field paths and their values from an object"""
        paths = defaultdict(list)

        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{prefix}.{key}" if prefix else key
                paths[current_path].append(value)

                # Recursively process nested objects
                if isinstance(value, dict):
                    nested_paths = self._get_nested_paths(value, current_path)
                    for nested_path, nested_values in nested_paths.items():
                        paths[nested_path].extend(nested_values)
                elif isinstance(value, list) and value:
                    # Handle arrays - analyze first element if it's an object
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            array_path = f"{current_path}[{i}]"
                            nested_paths = self._get_nested_paths(item, array_path)
                            for nested_path, nested_values in nested_paths.items():
                                paths[nested_path].extend(nested_values)
                        else:
                            # For primitive arrays, collect all values under the array path
                            array_path = f"{current_path}[]"
                            paths[array_path].append(item)

        return paths

    def _infer_field_type(self, values: List[Any]) -> str:
        """Infer the most appropriate type for a field based on sample values"""
        if not values:
            return "null"

        # Filter out null values for type inference
        non_null_values = [v for v in values if v is not None]
        if not non_null_values:
            return "null"

        # Get types of all non-null values
        types = [self._infer_type_from_value(v) for v in non_null_values]
        type_counts = defaultdict(int)
        for t in types:
            type_counts[t] += 1

        # Return the most common type
        return max(type_counts.items(), key=lambda x: x[1])[0]

    def _calculate_null_percentage(self, values: List[Any]) -> float:
        """Calculate percentage of null values"""
        if not values:
            return 100.0
        null_count = sum(1 for v in values if v is None)
        return (null_count / len(values)) * 100.0

    def _estimate_cardinality(self, values: List[Any]) -> str:
        """Estimate cardinality of field values"""
        if not values:
            return "unknown"

        # Filter out null values
        non_null_values = [v for v in values if v is not None]
        if not non_null_values:
            return "unknown"

        unique_count = len(set(str(v) for v in non_null_values))
        total_count = len(non_null_values)

        uniqueness_ratio = unique_count / total_count

        if uniqueness_ratio > 0.9:
            return "high"
        elif uniqueness_ratio > 0.5:
            return "medium"
        else:
            return "low"

    def _is_potential_message_key(self, field_path: str, values: List[Any]) -> bool:
        """Determine if a field could be used as a message key"""
        # Only top-level fields can be message keys
        if "." in field_path or "[" in field_path:
            return False

        # Must have high cardinality and low null percentage
        cardinality = self._estimate_cardinality(values)
        null_percentage = self._calculate_null_percentage(values)

        return cardinality == "high" and null_percentage < 10.0

    def _is_potential_foreign_key(self, field_path: str, values: List[Any]) -> bool:
        """Determine if a field could be a foreign key"""
        # Heuristic: ends with _id and not the primary message key
        field_name = field_path.split(".")[-1].split("[")[0]  # Get the actual field name
        if not field_name.endswith("_id"):
            return False

        # Should have reasonable cardinality and low null percentage
        cardinality = self._estimate_cardinality(values)
        null_percentage = self._calculate_null_percentage(values)

        return cardinality in ["medium", "high"] and null_percentage < 50.0

    def _get_examples(self, values: List[Any], max_examples: int) -> List[Any]:
        """Get representative examples from field values"""
        if not values:
            return []

        # Filter out null values
        non_null_values = [v for v in values if v is not None]
        if not non_null_values:
            return []

        # Get unique values
        unique_values = []
        seen = set()
        for value in non_null_values:
            value_str = str(value)
            if value_str not in seen:
                unique_values.append(value)
                seen.add(value_str)
                if len(unique_values) >= max_examples:
                    break

        return unique_values

    def _infer_schema_from_sample(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """Infer JSON schema structure from a single sample"""
        if not isinstance(sample, dict):
            return {"type": self._infer_type_from_value(sample)}

        schema = {"type": "object", "properties": {}, "required": []}

        for key, value in sample.items():
            if isinstance(value, dict):
                schema["properties"][key] = self._infer_schema_from_sample(value)
            elif isinstance(value, list) and value:
                # Analyze array items
                first_item = value[0]
                if isinstance(first_item, dict):
                    schema["properties"][key] = {"type": "array", "items": self._infer_schema_from_sample(first_item)}
                else:
                    schema["properties"][key] = {"type": "array", "items": {"type": self._infer_type_from_value(first_item)}}
            else:
                schema["properties"][key] = {"type": self._infer_type_from_value(value)}

            # Add to required if value is not None
            if value is not None:
                schema["required"].append(key)

        return schema

    def generate_field_analysis(self, messages: List[Dict[str, Any]], topic_spec) -> Dict[str, KafkaFieldAnalysis]:
        """Generate field-level analysis for messages"""
        if not self.schema_config.generate:
            return {}

        logger.info(f"Generating field analysis for {len(messages)} messages")

        # Extract all field paths and their values
        all_field_values = defaultdict(list)

        for message in messages:
            if isinstance(message, dict):
                field_paths = self._get_nested_paths(message)
                for path, values in field_paths.items():
                    all_field_values[path].extend(values)

        # Filter fields if specified in topic spec
        effective_fields = self.config_parser.get_effective_fields(topic_spec)
        if effective_fields:
            # Filter to only include specified fields
            filtered_field_values = {}
            for field in effective_fields:
                if field in all_field_values:
                    filtered_field_values[field] = all_field_values[field]
            all_field_values = filtered_field_values

        # Generate analysis for each field
        field_analysis = {}
        max_examples = self.schema_config.max_examples_per_field

        for field_path, values in all_field_values.items():
            # Infer type
            inferred_type = self._infer_field_type(values)

            # Get examples
            examples = []
            if self.schema_config.include_examples:
                examples = self._get_examples(values, max_examples)

            # Build analysis data
            analysis_data = {}

            if self.schema_config.analysis.calculate_null_percentage:
                analysis_data["null_percentage"] = self._calculate_null_percentage(values)

            if self.schema_config.analysis.estimate_cardinality:
                analysis_data["cardinality"] = self._estimate_cardinality(values)

            # Add potential key detection
            if self._is_potential_message_key(field_path, values):
                analysis_data["potential_message_key"] = True

            if self._is_potential_foreign_key(field_path, values):
                analysis_data["potential_foreign_key"] = True

            field_analysis[field_path] = KafkaFieldAnalysis(inferred_type=inferred_type, examples=examples, analysis=analysis_data)

        logger.info(f"Generated field analysis for {len(field_analysis)} fields")
        return field_analysis

    def infer_schema(self, messages: List[Dict[str, Any]]) -> Optional[KafkaInferredSchema]:
        """Infer JSON schema from sample messages"""
        if not self.schema_config.generate or not messages:
            return None

        logger.info(f"Inferring schema from {len(messages)} messages")

        # Start with the first message as base schema
        base_schema = None
        valid_messages = [msg for msg in messages if isinstance(msg, dict)]

        if not valid_messages:
            logger.warning("No valid dictionary messages found for schema inference")
            return None

        # Use the first message to establish the base structure
        base_schema = self._infer_schema_from_sample(valid_messages[0])

        # For a more comprehensive schema, we could merge multiple samples
        # but for simplicity, we'll use the first valid message as the template

        return KafkaInferredSchema(type=base_schema.get("type", "object"), properties=base_schema.get("properties"), required=base_schema.get("required"))

    def generate_topic_analysis(self, topic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis for a topic"""
        topic_name = topic_data["topic_name"]
        messages = topic_data["sample_messages"]
        topic_spec = topic_data["topic_spec"]

        logger.info(f"Generating analysis for topic {topic_name}")

        # Generate schema inference
        inferred_schema = self.infer_schema(messages)

        # Generate field analysis
        field_analysis = self.generate_field_analysis(messages, topic_spec)

        return {
            "topic_name": topic_name,
            "partitions": topic_data["partitions"],
            "inferred_schema": inferred_schema,
            "sample_messages": messages,
            "field_analysis": field_analysis,
        }
