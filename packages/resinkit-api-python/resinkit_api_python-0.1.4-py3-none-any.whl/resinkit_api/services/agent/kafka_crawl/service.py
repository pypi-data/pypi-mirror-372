import asyncio
from datetime import datetime, timezone
from typing import List

from resinkit_api.core.logging import get_logger
from resinkit_api.services.agent.kafka_crawl.config_parser import KafkaConfigParser
from resinkit_api.services.agent.kafka_crawl.consumer import KafkaMessageConsumer
from resinkit_api.services.agent.kafka_crawl.models import (
    KafkaCrawlConfig,
    KafkaCrawlResult,
    KafkaRetrievalMetadata,
    KafkaTopicCrawlResult,
)
from resinkit_api.services.agent.kafka_crawl.schema_inferrer import SchemaInferrer

logger = get_logger(__name__)


class KafkaCrawlService:
    """Main service orchestrating the Kafka message crawl operation"""

    async def execute_crawl(self, config: KafkaCrawlConfig) -> KafkaCrawlResult:
        """Execute a complete Kafka message crawl operation"""
        logger.info(f"Starting Kafka crawl for source: {config.kafka_source.bootstrap_servers}")

        try:
            # Initialize components
            config_parser = KafkaConfigParser(config)
            consumer = KafkaMessageConsumer(config_parser)
            schema_inferrer = SchemaInferrer(config_parser)

            # Validate configuration early to prevent background processes from starting
            regex_errors = config_parser.validate_regex_patterns()
            if regex_errors:
                raise ValueError(f"Configuration validation failed: {', '.join(regex_errors)}")

            # Additional validation: check for common misconfigurations
            topic_validation_errors = self._validate_topic_specifications(config_parser)
            if topic_validation_errors:
                raise ValueError(f"Topic specification validation failed: {', '.join(topic_validation_errors)}")

            # Execute crawl with timeout
            logger.info("Starting topic crawl...")
            try:
                crawled_topics = await asyncio.wait_for(consumer.crawl_all_topics(), timeout=30.0)
            except asyncio.TimeoutError:
                logger.error("Kafka crawl operation timed out - Kafka cluster may be unavailable")
                raise Exception("Kafka crawl operation timed out")

            if not crawled_topics:
                raise Exception("No topics were successfully crawled")

            # Generate schema analysis
            logger.info("Generating schema analysis...")
            analyzed_topics = []
            for topic_data in crawled_topics:
                try:
                    analyzed_topic = schema_inferrer.generate_topic_analysis(topic_data)
                    analyzed_topics.append(analyzed_topic)
                except Exception as e:
                    logger.error(f"Failed to analyze topic {topic_data.get('topic_name', 'unknown')}: {str(e)}")
                    # Include topic without analysis
                    analyzed_topics.append(
                        {
                            "topic_name": topic_data["topic_name"],
                            "partitions": topic_data["partitions"],
                            "inferred_schema": None,
                            "sample_messages": topic_data["sample_messages"],
                            "field_analysis": {},
                        }
                    )

            result = self._build_result(config_parser, analyzed_topics)

            logger.info(f"Kafka crawl completed successfully. Crawled {len(analyzed_topics)} topics.")
            return result

        except ValueError as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Kafka crawl failed: {str(e)}")
            raise Exception(f"Kafka crawl operation failed: {str(e)}")

    def _validate_topic_specifications(self, config_parser: KafkaConfigParser) -> List[str]:
        """Validate topic specifications for common misconfigurations"""
        errors = []

        topic_specs = config_parser.get_topic_specifications()

        for i, topic_spec in enumerate(topic_specs):
            if hasattr(topic_spec, "name"):  # TopicSelection
                topic_name = topic_spec.name

                # Check for regex-like patterns in direct topic names
                if self._looks_like_regex_pattern(topic_name):
                    errors.append(
                        f"Topic #{i+1}: Topic name '{topic_name}' appears to be a regex pattern but is configured as a direct topic name. Use 'name_regex' field in TopicRegexSelection instead of 'name' field in TopicSelection."
                    )

                # Check for empty or whitespace-only topic names
                if not topic_name.strip():
                    errors.append(f"Topic #{i+1}: Topic name cannot be empty or whitespace-only")

        return errors

    def _looks_like_regex_pattern(self, topic_name: str) -> bool:
        """Check if a topic name looks like it might be intended as a regex pattern"""
        # Common regex patterns that users might accidentally use as topic names
        regex_indicators = [
            "*",  # Wildcard
            ".",  # Any character (especially when combined with *)
            "?",  # Optional
            "+",  # One or more
            "^",  # Start anchor
            "$",  # End anchor
            "[",  # Character class
            "]",  # Character class end
            "(",  # Group
            ")",  # Group end
            "|",  # Alternation
            "\\",  # Escape
        ]

        # Check for standalone common patterns
        if topic_name in [".*", "*", "?", "+", "^", "$"]:
            return True

        # Check for regex special characters
        for indicator in regex_indicators:
            if indicator in topic_name:
                return True

        return False

    def _build_result(self, config_parser: KafkaConfigParser, analyzed_topics: List[dict]) -> KafkaCrawlResult:
        """Build the final crawl result"""

        # Create metadata
        metadata = KafkaRetrievalMetadata(
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            kafka_source=config_parser.get_kafka_source().bootstrap_servers,
            config_hash=config_parser.get_config_hash(),
        )

        # Convert topic data to result models
        topic_results = []
        for topic_data in analyzed_topics:
            topic_result = KafkaTopicCrawlResult(
                topic_name=topic_data["topic_name"],
                partitions=topic_data["partitions"],
                inferred_schema=topic_data.get("inferred_schema"),
                sample_messages=topic_data["sample_messages"],
                field_analysis=topic_data.get("field_analysis"),
            )
            topic_results.append(topic_result)

        return KafkaCrawlResult(retrieval_metadata=metadata, topics=topic_results)
