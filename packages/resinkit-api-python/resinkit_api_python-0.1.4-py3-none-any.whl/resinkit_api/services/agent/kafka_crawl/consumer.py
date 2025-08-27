import asyncio
import json
from typing import Any, Dict, List, Union

from aiokafka import AIOKafkaConsumer, TopicPartition
from aiokafka.admin import AIOKafkaAdminClient

from resinkit_api.core.logging import get_logger
from resinkit_api.services.agent.kafka_crawl.config_parser import KafkaConfigParser
from resinkit_api.services.agent.kafka_crawl.models import (
    TopicRegexSelection,
    TopicSelection,
    ValueDeserializer,
)

logger = get_logger(__name__)

# Configuration for batch processing
KAFKA_CRAWL_BATCH = 30  # Number of topics to crawl concurrently in each batch


class KafkaMessageConsumer:
    """Consumer for Kafka messages with configurable sampling strategies"""

    def __init__(self, config_parser: KafkaConfigParser):
        self.config_parser = config_parser
        self.kafka_source = config_parser.get_kafka_source()

    def _build_consumer_config(self) -> Dict[str, Any]:
        """Build Kafka consumer configuration"""
        config = {
            "bootstrap_servers": self.kafka_source.bootstrap_servers,
            "auto_offset_reset": "latest",  # Will be overridden per topic
            "enable_auto_commit": False,
            "consumer_timeout_ms": self.config_parser.get_consumer_timeout_ms(),
            "request_timeout_ms": 10000,  # 10 second timeout for requests
            "connections_max_idle_ms": 5000,  # Close idle connections quickly
            "metadata_max_age_ms": 5000,  # Refresh metadata quickly
        }

        # Add security configuration if provided
        if self.kafka_source.security_protocol:
            config["security_protocol"] = self.kafka_source.security_protocol

        if self.kafka_source.sasl_mechanism:
            config["sasl_mechanism"] = self.kafka_source.sasl_mechanism

        if self.kafka_source.sasl_username and self.kafka_source.sasl_password:
            config["sasl_plain_username"] = self.kafka_source.sasl_username
            config["sasl_plain_password"] = self.kafka_source.sasl_password

        return config

    def _build_admin_config(self) -> Dict[str, Any]:
        """Build Kafka admin client configuration"""
        config = {
            "bootstrap_servers": self.kafka_source.bootstrap_servers,
            "request_timeout_ms": 10000,  # 10 second timeout for requests
            "connections_max_idle_ms": 5000,  # Close idle connections quickly
            "metadata_max_age_ms": 5000,  # Refresh metadata quickly
        }

        # Add security configuration if provided
        if self.kafka_source.security_protocol:
            config["security_protocol"] = self.kafka_source.security_protocol

        if self.kafka_source.sasl_mechanism:
            config["sasl_mechanism"] = self.kafka_source.sasl_mechanism

        if self.kafka_source.sasl_username and self.kafka_source.sasl_password:
            config["sasl_plain_username"] = self.kafka_source.sasl_username
            config["sasl_plain_password"] = self.kafka_source.sasl_password

        return config

    async def get_available_topics(self) -> List[str]:
        """Get list of available topics from Kafka cluster"""
        admin_config = self._build_admin_config()

        try:
            admin_client = AIOKafkaAdminClient(**admin_config)

            # Add timeout to admin client start
            try:
                await asyncio.wait_for(admin_client.start(), timeout=10.0)  # 10 second timeout
            except asyncio.TimeoutError:
                logger.error("Timeout connecting to Kafka cluster for topic discovery")
                return []

            try:
                # Add timeout to list_topics operation
                topic_names = await asyncio.wait_for(admin_client.list_topics(), timeout=10.0)
                logger.info(f"Found {len(topic_names)} topics in Kafka cluster")
                return topic_names
            except asyncio.TimeoutError:
                logger.error("Timeout getting topics list")
                return []
            finally:
                await admin_client.close()

        except Exception as e:
            logger.error(f"Failed to get available topics: {str(e)}")
            return []

    async def get_topic_partitions(self, topic_name: str) -> int:
        """Get number of partitions for a topic"""
        # Validate topic name before attempting connection
        if self._is_invalid_topic_name(topic_name):
            logger.error(f"Invalid topic name '{topic_name}' - topic names cannot contain regex special characters")
            raise Exception(f"Invalid topic name '{topic_name}' - appears to be a regex pattern")

        consumer_config = self._build_consumer_config()
        consumer = None

        try:
            # Use a consumer to get topic partition metadata
            consumer = AIOKafkaConsumer(topic_name, **consumer_config)

            # Add timeout to consumer start
            try:
                await asyncio.wait_for(consumer.start(), timeout=10.0)
            except asyncio.TimeoutError:
                logger.error(f"Timeout connecting to Kafka cluster for topic {topic_name} metadata")
                raise Exception(f"Kafka cluster unavailable - timeout connecting for topic {topic_name}")

            try:
                # Get topic partitions using consumer metadata after subscribing
                partitions = consumer.partitions_for_topic(topic_name)
                if partitions is None:
                    logger.warning(f"Topic '{topic_name}' not found")
                    raise Exception(f"Topic '{topic_name}' does not exist in the Kafka cluster")
                return len(partitions)
            finally:
                # Ensure consumer is always stopped
                if consumer:
                    try:
                        await asyncio.wait_for(consumer.stop(), timeout=5.0)
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout stopping consumer for topic {topic_name}")
                    except Exception as stop_error:
                        logger.warning(f"Error stopping consumer for topic {topic_name}: {str(stop_error)}")

        except Exception as e:
            # Ensure consumer cleanup even on exception
            if consumer:
                try:
                    await asyncio.wait_for(consumer.stop(), timeout=2.0)
                except Exception as cleanup_error:
                    logger.warning(f"Error during consumer cleanup for topic {topic_name}: {str(cleanup_error)}")

            logger.error(f"Failed to get partition count for topic {topic_name}: {str(e)}")
            # If the error message indicates cluster unavailability, propagate it
            if "Kafka cluster unavailable" in str(e) or "timeout connecting" in str(e).lower() or "does not exist" in str(e):
                raise e
            return 0

    def _is_invalid_topic_name(self, topic_name: str) -> bool:
        """Check if topic name contains invalid characters that suggest it's a regex pattern"""
        # Common regex characters that indicate the user meant to use a regex pattern
        invalid_chars = ["*", "?", "+", "^", "$", "[", "]", "(", ")", "|", "\\"]

        # Check for standalone regex patterns like ".*" or "*"
        if topic_name in [".*", "*", "?", "+"]:
            return True

        # Check for regex special characters
        for char in invalid_chars:
            if char in topic_name:
                return True

        return False

    def _deserialize_message_value(self, value: bytes, deserializer: str) -> Any:
        """Deserialize message value based on configured deserializer"""
        if value is None:
            return None

        try:
            if deserializer == ValueDeserializer.JSON.value:
                return json.loads(value.decode("utf-8"))
            elif deserializer == ValueDeserializer.STRING.value:
                return value.decode("utf-8")
            elif deserializer == ValueDeserializer.AVRO.value:
                # For now, treat as string - would need schema registry integration
                logger.warning("Avro deserialization not fully implemented, treating as string")
                return value.decode("utf-8")
            elif deserializer == ValueDeserializer.PROTOBUF.value:
                # For now, treat as string - would need protobuf schema
                logger.warning("Protobuf deserialization not fully implemented, treating as string")
                return value.decode("utf-8")
            else:
                return value.decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to deserialize message value: {str(e)}")
            return None

    async def consume_messages_from_topic(self, topic_name: str, topic_spec: Union[TopicSelection, TopicRegexSelection]) -> List[Dict[str, Any]]:
        """Consume messages from a specific topic"""
        # Validate topic name before attempting connection
        if self._is_invalid_topic_name(topic_name):
            logger.error(f"Invalid topic name '{topic_name}' - topic names cannot contain regex special characters")
            raise Exception(f"Invalid topic name '{topic_name}' - appears to be a regex pattern")

        sample_count = self.config_parser.get_effective_sample_messages(topic_spec)
        sampling_strategy = self.config_parser.get_effective_sampling_strategy(topic_spec)
        deserializer = self.config_parser.get_value_deserializer(topic_spec)

        logger.info(f"Consuming {sample_count} messages from topic '{topic_name}' using {sampling_strategy} strategy")

        consumer_config = self._build_consumer_config()
        consumer_config["auto_offset_reset"] = "earliest"  # Always use earliest to allow seeking
        consumer = None

        try:
            consumer = AIOKafkaConsumer(**consumer_config)

            # Add timeout to consumer start to fail fast if Kafka is unavailable
            try:
                await asyncio.wait_for(consumer.start(), timeout=self.config_parser.get_consumer_timeout_ms())
            except asyncio.TimeoutError:
                logger.error(f"Timeout starting consumer for topic {topic_name} - Kafka cluster may be unavailable")
                raise Exception(f"Kafka cluster unavailable - timeout connecting for topic {topic_name}")

            # Get all partitions for the topic
            partitions = consumer.partitions_for_topic(topic_name)
            if not partitions:
                logger.warning(f"No partitions found for topic {topic_name}")
                return []

            # Create TopicPartition objects
            topic_partitions = [TopicPartition(topic_name, partition) for partition in partitions]
            consumer.assign(topic_partitions)

            # Handle different sampling strategies with seek operations
            if sampling_strategy == "latest_offset":
                # Seek to end minus sample_count for latest messages
                end_offsets = await consumer.end_offsets(topic_partitions)
                messages_per_partition = max(1, sample_count // len(topic_partitions))

                for tp in topic_partitions:
                    end_offset = end_offsets[tp]
                    if end_offset > 0:
                        # Seek to get the last N messages
                        start_offset = max(0, end_offset - messages_per_partition)
                        consumer.seek(tp, start_offset)
            elif sampling_strategy == "earliest":
                # Seek to beginning for earliest messages
                beginning_offsets = await consumer.beginning_offsets(topic_partitions)
                for tp in topic_partitions:
                    consumer.seek(tp, beginning_offsets[tp])
            else:
                # Default to earliest
                beginning_offsets = await consumer.beginning_offsets(topic_partitions)
                for tp in topic_partitions:
                    consumer.seek(tp, beginning_offsets[tp])

            # Use getmany to consume existing messages without waiting
            message_batch = await consumer.getmany(
                *topic_partitions,
                timeout_ms=self.config_parser.get_consumer_timeout_ms(),
                max_records=sample_count,  # Get all sample messages at once
            )

            all_messages = []
            # Process messages from all partitions
            for tp, messages in message_batch.items():
                for message in messages:
                    if len(all_messages) >= sample_count:
                        break

                    try:
                        # Deserialize the message value
                        deserialized_value = self._deserialize_message_value(message.value, deserializer)

                        if deserialized_value is not None:
                            message_data = {
                                "value": deserialized_value,
                                "partition": message.partition,
                                "offset": message.offset,
                                "timestamp": message.timestamp,
                            }

                            # Add key if present
                            if message.key:
                                message_data["key"] = message.key.decode("utf-8")

                            all_messages.append(message_data)
                            logger.debug(f"Consumed message from {topic_name}, partition {message.partition}, offset {message.offset}")

                    except Exception as e:
                        logger.error(f"Error processing message from {topic_name}: {str(e)}")
                        continue

            # For latest_offset strategy, sort by timestamp to get the most recent
            if sampling_strategy == "latest_offset":
                all_messages.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
                all_messages = all_messages[:sample_count]

            logger.info(f"Successfully consumed {len(all_messages)} messages from topic '{topic_name}'")
            return all_messages

        except Exception as e:
            logger.error(f"Failed to consume messages from topic {topic_name}: {str(e)}")
            # If the error message indicates cluster unavailability, propagate it
            if "Kafka cluster unavailable" in str(e) or "timeout connecting" in str(e).lower() or "appears to be a regex pattern" in str(e):
                raise e
            return []
        finally:
            # Ensure consumer is always stopped
            if consumer:
                try:
                    await asyncio.wait_for(consumer.stop(), timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout stopping consumer for topic {topic_name}")
                except Exception as stop_error:
                    logger.warning(f"Error stopping consumer for topic {topic_name}: {str(stop_error)}")

    async def crawl_topic(self, topic_name: str, topic_spec: Union[TopicSelection, TopicRegexSelection]) -> Dict[str, Any]:
        """Simplified topic crawling"""
        logger.info(f"Crawling topic: {topic_name}")

        try:
            # Consume sample messages (this also validates topic existence)
            messages = await self.consume_messages_from_topic(topic_name, topic_spec)

            # Count partitions from consumed messages if any, otherwise use dedicated method
            partitions_from_messages = set()
            if messages:
                partitions_from_messages = {msg["partition"] for msg in messages if "partition" in msg}
                partition_count = len(partitions_from_messages) if partitions_from_messages else await self.get_topic_partitions(topic_name)
            else:
                partition_count = await self.get_topic_partitions(topic_name)

            # Extract just the message values for analysis
            sample_messages = [msg["value"] for msg in messages if "value" in msg]

            return {"topic_name": topic_name, "partitions": partition_count, "sample_messages": sample_messages, "topic_spec": topic_spec}

        except Exception as e:
            logger.error(f"Failed to crawl topic {topic_name}: {str(e)}")
            raise Exception(f"Topic crawl failed for {topic_name}: {str(e)}")

    async def crawl_all_topics(self, timeout: float = 60.0) -> List[Dict[str, Any]]:
        """Crawl all configured topics"""
        topic_specs = self.config_parser.get_topic_specifications()

        # For specific topic names, try to crawl them directly
        # For regex patterns, we need to discover available topics first
        direct_topics = []
        regex_specs = []

        for spec in topic_specs:
            if hasattr(spec, "name"):  # TopicSelection
                direct_topics.append((spec.name, spec))
            else:  # TopicRegexSelection
                regex_specs.append(spec)

        # Handle regex specifications by discovering topics
        regex_resolved = []
        if regex_specs:
            try:
                # Add timeout to topic discovery to fail fast
                available_topics = await asyncio.wait_for(self.get_available_topics(), timeout=timeout)
                if available_topics:
                    for regex_spec in regex_specs:
                        resolved = self.config_parser.resolve_topic_selection(available_topics)
                        regex_resolved.extend([(name, spec) for name, spec in resolved if spec == regex_spec])
                else:
                    logger.warning("Could not discover topics for regex matching - Kafka cluster may be unavailable")
            except asyncio.TimeoutError:
                logger.error("Timeout during topic discovery - Kafka cluster may be unavailable")
                raise Exception("Kafka cluster connection timeout during topic discovery")

        # Combine direct topics and regex-resolved topics
        all_topics_to_crawl = direct_topics + regex_resolved

        if not all_topics_to_crawl:
            raise Exception("No topics specified for crawling")

        logger.info(f"Will attempt to crawl {len(all_topics_to_crawl)} topics")

        # Crawl topics in batches with concurrent processing within each batch
        crawled_topics = []

        # Process topics in batches
        n_batches = (len(all_topics_to_crawl) + KAFKA_CRAWL_BATCH - 1) // KAFKA_CRAWL_BATCH
        batch_timeout = (timeout / n_batches) * 0.8
        for i in range(0, len(all_topics_to_crawl), KAFKA_CRAWL_BATCH):
            batch = all_topics_to_crawl[i : i + KAFKA_CRAWL_BATCH]
            batch_size = len(batch)
            logger.info(
                f"Processing batch {i//KAFKA_CRAWL_BATCH + 1}/{(len(all_topics_to_crawl) + KAFKA_CRAWL_BATCH - 1)//KAFKA_CRAWL_BATCH} with {batch_size} topics"
            )

            # Create concurrent tasks for this batch
            batch_tasks = []
            for topic_name, topic_spec in batch:
                task = asyncio.create_task(asyncio.wait_for(self.crawl_topic(topic_name, topic_spec), timeout=batch_timeout), name=f"crawl_{topic_name}")
                batch_tasks.append((task, topic_name))

            # Wait for all tasks in this batch to complete
            batch_results = await asyncio.gather(*[task for task, _ in batch_tasks], return_exceptions=True)

            # Process results from this batch
            for result, (_, topic_name) in zip(batch_results, batch_tasks):
                if isinstance(result, asyncio.TimeoutError):
                    logger.error(f"Timeout crawling topic {topic_name} - continuing with other topics")
                elif isinstance(result, Exception):
                    logger.error(f"Failed to crawl topic {topic_name}: {str(result)}")
                else:
                    # Successful result
                    crawled_topics.append(result)

            logger.info(
                f"Completed batch {i//KAFKA_CRAWL_BATCH + 1}, successfully crawled {len([r for r in batch_results if not isinstance(r, Exception)])} out of {batch_size} topics"
            )

        if not crawled_topics:
            raise Exception("Failed to crawl any topics - topics may not exist or Kafka cluster may be unavailable")

        logger.info(f"Successfully crawled {len(crawled_topics)} topics")
        return crawled_topics
