"""
MCP prompts for Flink SQL development

This module provides MCP prompts that help AI agents generate high-quality Flink SQL
following established best practices and avoiding common mistakes.
"""

from pydantic import Field

from resinkit_api.apps import get_mcp
from resinkit_api.core.logging import get_logger

logger = get_logger(__name__)
mcp = get_mcp()


@mcp.prompt
def flink_sql_best_practices(
    task_description: str = Field(..., description="Description of the Flink SQL task to be implemented"),
    use_case: str = Field("streaming", description="Use case type: 'streaming', 'batch', or 'hybrid'"),
    source_type: str = Field("kafka", description="Primary source type: 'kafka', 'mysql', 'datagen', 'paimon', etc."),
    sink_type: str = Field("kafka", description="Primary sink type: 'kafka', 'mysql', 'paimon', 'filesystem', etc."),
    include_examples: bool = Field(True, description="Whether to include relevant code examples"),
) -> str:
    """
    Generate comprehensive Flink SQL best practices prompt for AI agents.

    This prompt provides essential guidance for writing high-quality Flink SQL that follows
    established patterns, avoids common mistakes, and implements proper resource management.
    Use this prompt before generating any Flink SQL to ensure quality and consistency.

    Args:
        task_description: Description of the Flink SQL task to be implemented
        use_case: Use case type - 'streaming', 'batch', or 'hybrid'
        source_type: Primary source type like 'kafka', 'mysql', 'datagen', 'paimon'
        sink_type: Primary sink type like 'kafka', 'mysql', 'paimon', 'filesystem'
        include_examples: Whether to include relevant code examples

    Returns:
        Comprehensive prompt with Flink SQL best practices and guidelines
    """

    prompt = (
        f"""# Flink SQL Best Practices Guide

You are about to generate Flink SQL for the following task:
**Task Description:** {task_description}
**Use Case:** {use_case}
**Source Type:** {source_type}
**Sink Type:** {sink_type}

## CRITICAL: Reserved Words and Identifiers

**ALWAYS avoid using reserved words as column names.** If you must use reserved words, surround them with backticks.

**Reserved words include (partial list):**
```
SELECT, FROM, WHERE, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, TABLE, INDEX, PRIMARY, KEY, 
FOREIGN, REFERENCES, CONSTRAINT, UNIQUE, NOT, NULL, DEFAULT, AUTO_INCREMENT, ENGINE, CHARSET,
COUNT, SUM, AVG, MIN, MAX, GROUP, ORDER, BY, HAVING, DISTINCT, UNION, JOIN, INNER, LEFT, RIGHT,
FULL, OUTER, ON, AS, CASE, WHEN, THEN, ELSE, END, IF, EXISTS, IN, BETWEEN, LIKE, IS, AND, OR,
TRUE, FALSE, CURRENT_TIME, CURRENT_DATE, CURRENT_TIMESTAMP, USER, SYSTEM_USER, SESSION_USER,
INTERVAL, YEAR, MONTH, DAY, HOUR, MINUTE, SECOND, TIMESTAMP, DATE, TIME, DATETIME, VARCHAR,
CHAR, TEXT, INT, INTEGER, BIGINT, SMALLINT, TINYINT, DECIMAL, NUMERIC, FLOAT, DOUBLE, BOOLEAN,
BINARY, VARBINARY, BLOB, ARRAY, MAP, ROW, MULTISET, VALUE, VALUES, PARTITION, WINDOW, OVER,
PRECEDING, FOLLOWING, UNBOUNDED, CURRENT, ROWS, RANGE
```

**Safe alternatives:**
- `value` → `val`, `amount`, `measurement`
- `count` → `cnt`, `total_count`, `record_count`
- `order` → `sort_order`, `sequence_num`
- `user` → `user_id`, `username`, `customer`
- `date` → `event_date`, `created_date`, `process_date`

## Data Types - Use Only Supported Types

**Character Strings:**
- `VARCHAR(n)`, `STRING` (VARCHAR(2147483647))
- `CHAR(n)` for fixed-length

**Binary Strings:**
- `VARBINARY(n)`, `BYTES` (VARBINARY(2147483647))
- `BINARY(n)` for fixed-length

**Exact Numerics:**
- `TINYINT` (-128 to 127)
- `SMALLINT` (-32,768 to 32,767)
- `INT`, `INTEGER` (-2,147,483,648 to 2,147,483,647)
- `BIGINT` (-9,223,372,036,854,775,808 to 9,223,372,036,854,775,807)
- `DECIMAL(p, s)`, `NUMERIC(p, s)` (p=1-38, s=0-p)

**Approximate Numerics:**
- `FLOAT` (4-byte)
- `DOUBLE`, `DOUBLE PRECISION` (8-byte)

**Date and Time:**
- `DATE` (0000-01-01 to 9999-12-31)
- `TIME(p)` (p=0-9 fractional seconds)
- `TIMESTAMP(p)` (p=0-9 fractional seconds, default=6)
- `TIMESTAMP(p) WITH TIME ZONE`
- `TIMESTAMP_LTZ(p)` (local time zone)

**Other Types:**
- `BOOLEAN` (TRUE, FALSE, UNKNOWN)
- `ARRAY<type>`
- `MAP<key_type, value_type>`
- `ROW<field1 type1, field2 type2, ...>`

## Essential Configuration Patterns

**For Streaming Jobs:**
```sql
-- Set checkpointing interval (REQUIRED for streaming)
SET 'execution.checkpointing.interval' = '60s';
-- Alternative intervals: '30s', '5s', '2min'
```

**For Batch Jobs:**
```sql
-- Explicitly set batch mode
SET 'execution.runtime-mode' = 'batch';
-- Remove checkpointing for batch
RESET 'execution.checkpointing.interval';
```

**For Hybrid Jobs (streaming with finite sources):**
```sql
-- Set checkpointing for streaming sections
SET 'execution.checkpointing.interval' = '30s';
-- Switch to batch for OLAP queries
RESET 'execution.checkpointing.interval';
SET 'execution.runtime-mode' = 'batch';
```


## Variable Substitution

**Use only ${{variable}} syntax:**
- ✅ `'password' = '${{MYSQL_PASSWORD}}'`
- ✅ `'warehouse' = 'file:/tmp/paimon_${{__NOW_TS10__}}'`
- ❌ `#{{variable}}`, `%{{variable}}`, `${{variable}}`

** Variables need to be defined first.**
** System variables are defined by `__` prefix.**
- "__NOW_TS10__": 10-digit timestamp for uniqueness
- "__RANDOM_16BIT__": 16-bit random number
- "__SUUID_9__": 9-digit short UUID

## Common Anti-Patterns to Avoid

**❌ Don't use reserved words without backticks:**
```sql
-- BAD
CREATE TABLE orders (order INT, user STRING, count BIGINT);

-- GOOD
CREATE TABLE orders (order_id INT, user_id STRING, record_count BIGINT);
-- OR with backticks if unavoidable
CREATE TABLE orders (`order` INT, `user` STRING, `count` BIGINT);
```

**❌ Don't forget checkpointing for streaming:**
```sql
-- BAD - streaming job without checkpointing
CREATE TABLE kafka_source (...) WITH ('connector' = 'kafka', ...);
INSERT INTO sink_table SELECT * FROM kafka_source;

-- GOOD
SET 'execution.checkpointing.interval' = '60s';
CREATE TABLE kafka_source (...) WITH ('connector' = 'kafka', ...);
INSERT INTO sink_table SELECT * FROM kafka_source;
```

**❌ Don't use unsupported data types:**
```sql
-- BAD
CREATE TABLE bad_table (
    id SERIAL,           -- Not supported
    data JSON,           -- Not supported
    created DATETIME     -- Use TIMESTAMP(3) instead
);

-- GOOD
CREATE TABLE good_table (
    id INT,
    data STRING,         -- Use STRING for JSON-like data
    created TIMESTAMP(3)
);
```


## Pre-installed Dependencies

**These JARs are already available - DO NOT include in resources:**
- Flink Core: flink-dist-1.19.0.jar, flink-table-*.jar
- Formats: flink-json-1.19.0.jar, flink-csv-1.19.0.jar
- Paimon: paimon-flink-1.19-1.0.1.jar, paimon-flink-action-1.0.1.jar
- CDC: flink-cdc-dist-3.2.1.jar, flink-cdc-pipeline-connector-*.jar
- Logging: log4j-*.jar
- Hadoop: flink-shaded-hadoop-2-uber-2.8.3-10.0.jar

## Now Generate Your Flink SQL

Following the above guidelines, create a complete Flink SQL solution for: """
        + task_description
    )

    if include_examples and source_type.lower() == "kafka":
        prompt += """

## Kafka Example Reference

```sql

SET 'execution.checkpointing.interval' = '60s';

CREATE TABLE kafka_transactions (
    transaction_id STRING,
    sender_id INT,
    recipient_id INT,
    amount DECIMAL(10, 2),
    event_timestamp STRING,
    note STRING,
    transaction_type STRING,
    status STRING,
    fee DECIMAL(10, 2),
    kafka_record_ts TIMESTAMP(3) METADATA FROM 'timestamp'
) WITH (
    'connector' = 'kafka',
    'topic' = 'transactions_topic',
    'properties.bootstrap.servers' = '${{KAFKA_BROKERS_URL}}',
    'properties.group.id' = 'processor_${{__NOW_TS10__}}',
    'format' = 'json',
    'scan.startup.mode' = 'earliest-offset'
);

SELECT * FROM kafka_transactions WHERE amount > 100.00;

```"""

    if include_examples and source_type.lower() == "paimon":
        prompt += """

## Paimon Example Reference

```sql
CREATE CATALOG analytics_catalog WITH (
    'type' = 'paimon',
    'warehouse' = 'file:/tmp/paimon_${{__NOW_TS10__}}'
);

USE CATALOG analytics_catalog;

CREATE TABLE user_events (
    user_id BIGINT,
    event_type STRING,
    event_time TIMESTAMP(3),
    properties MAP<STRING, STRING>,
    dt STRING,
    PRIMARY KEY (dt, user_id) NOT ENFORCED
) PARTITIONED BY (dt) WITH (
    'bucket' = '4',
    'changelog-producer' = 'input'
);

-- For batch analysis
SET 'execution.runtime-mode' = 'batch';
SELECT user_id, COUNT(*) as event_count 
    FROM user_events 
    GROUP BY user_id;
```"""

    return prompt
