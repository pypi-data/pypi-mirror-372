import hashlib
import re
from typing import List, Union

from resinkit_api.core.logging import get_logger
from resinkit_api.services.agent.kafka_crawl.models import (
    KafkaCrawlConfig,
    TopicRegexSelection,
    TopicSelection,
)

logger = get_logger(__name__)


class KafkaConfigParser:
    """Parser for Kafka crawl configuration"""

    def __init__(self, config: KafkaCrawlConfig):
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

    def get_kafka_source(self):
        """Get the Kafka source configuration"""
        return self.config.kafka_source

    def get_default_settings(self):
        """Get the default settings"""
        return self.config.defaults

    def get_topic_specifications(self) -> List[Union[TopicSelection, TopicRegexSelection]]:
        """Get all topic specifications"""
        return self.config.topics

    def get_schema_inference_config(self):
        """Get schema inference configuration"""
        return self.config.schema_inference

    def validate_regex_patterns(self) -> List[str]:
        """Validate regex patterns in topic specifications and topic names"""
        errors = []

        for topic_spec in self.config.topics:
            if isinstance(topic_spec, TopicRegexSelection):
                try:
                    re.compile(topic_spec.name_regex)
                except re.error as e:
                    errors.append(f"Invalid regex pattern '{topic_spec.name_regex}': {str(e)}")
            elif isinstance(topic_spec, TopicSelection):
                # Validate that direct topic names don't look like regex patterns
                if self._looks_like_regex_pattern(topic_spec.name):
                    errors.append(
                        f"Topic name '{topic_spec.name}' appears to be a regex pattern. Use TopicRegexSelection with name_regex field instead of TopicSelection with name field"
                    )

        return errors

    def _looks_like_regex_pattern(self, topic_name: str) -> bool:
        """Check if a topic name looks like it might be intended as a regex pattern"""
        # Common regex characters that are unlikely to be valid Kafka topic names
        regex_indicators = [
            "*",  # Match zero or more
            ".",  # Match any character (when used alone or with *)
            "?",  # Match zero or one
            "+",  # Match one or more
            "^",  # Start anchor
            "$",  # End anchor
            "[",  # Character class start
            "]",  # Character class end
            "(",  # Group start
            ")",  # Group end
            "|",  # Alternation
            "\\",  # Escape character
        ]

        # Check for common regex patterns
        regex_patterns = [
            r"^\.\*$",  # Literal .*
            r"^\*$",  # Literal *
            r".*\.\*.*",  # Contains .*
            r".*\*.*",  # Contains *
            r".*\?.*",  # Contains ?
            r".*\+.*",  # Contains +
            r".*\^.*",  # Contains ^
            r".*\$.*",  # Contains $
            r".*\[.*\].*",  # Contains character class
            r".*\(.*\).*",  # Contains groups
            r".*\|.*",  # Contains alternation
        ]

        # Check for regex indicators
        for indicator in regex_indicators:
            if indicator in topic_name:
                return True

        # Check for regex patterns
        for pattern in regex_patterns:
            if re.match(pattern, topic_name):
                return True

        return False

    def resolve_topic_selection(self, available_topics: List[str]) -> List[tuple[str, Union[TopicSelection, TopicRegexSelection]]]:
        """
        Resolve topic specifications against available topics.
        Returns list of (topic_name, original_spec) tuples.
        """
        resolved_topics = []

        for topic_spec in self.config.topics:
            if isinstance(topic_spec, TopicSelection):
                # Direct topic name match
                if topic_spec.name in available_topics:
                    resolved_topics.append((topic_spec.name, topic_spec))
                else:
                    logger.warning(f"Topic '{topic_spec.name}' not found in available topics")

            elif isinstance(topic_spec, TopicRegexSelection):
                # Regex pattern matching
                try:
                    pattern = re.compile(topic_spec.name_regex)
                    matched_topics = [topic for topic in available_topics if pattern.match(topic)]

                    if matched_topics:
                        for topic_name in matched_topics:
                            resolved_topics.append((topic_name, topic_spec))
                    else:
                        logger.warning(f"No topics matched regex pattern '{topic_spec.name_regex}'")

                except re.error as e:
                    logger.error(f"Invalid regex pattern '{topic_spec.name_regex}': {str(e)}")

        return resolved_topics

    def get_effective_sample_messages(self, topic_spec: Union[TopicSelection, TopicRegexSelection]) -> int:
        """Get effective sample message count for a topic specification"""
        if topic_spec.sample_messages is not None:
            return topic_spec.sample_messages
        return self.config.defaults.sample_messages

    def get_effective_sampling_strategy(self, topic_spec: Union[TopicSelection, TopicRegexSelection]) -> str:
        """Get effective sampling strategy for a topic specification"""
        if topic_spec.sampling_strategy is not None:
            return topic_spec.sampling_strategy.value
        return self.config.defaults.sampling_strategy.value

    def get_effective_fields(self, topic_spec: Union[TopicSelection, TopicRegexSelection]) -> List[str]:
        """Get effective fields for a topic specification (None means all fields)"""
        return topic_spec.fields

    def get_value_deserializer(self, topic_spec: Union[TopicSelection, TopicRegexSelection]) -> str:
        """Get value deserializer for a topic specification"""
        return topic_spec.value_deserializer.value

    def should_generate_schema(self) -> bool:
        """Check if schema inference should be generated"""
        return self.config.schema_inference.generate

    def get_consumer_timeout_ms(self) -> int:
        """Get consumer timeout in milliseconds"""
        return self.config.defaults.consumer_timeout_ms
