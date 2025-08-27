import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from resinkit_api.core.config import settings
from resinkit_api.core.logging import get_logger
from resinkit_api.services.agent.db_crawl.config_parser import ConfigParser
from resinkit_api.services.agent.db_crawl.crawler import DatabaseCrawler
from resinkit_api.services.agent.db_crawl.dsds_generator import DSDSGenerator
from resinkit_api.services.agent.db_crawl.models import (
    DbCrawlConfig,
    DbCrawlResult,
    RetrievalMetadata,
    TableCrawlResult,
)

logger = get_logger(__name__)


class DatabaseCrawlService:
    """Main service orchestrating the database crawl operation"""

    async def execute_crawl(self, db: Session, config: DbCrawlConfig, save_remote: bool = True) -> DbCrawlResult:
        """Execute a complete database crawl operation"""
        logger.info(f"Starting database crawl for source: {config.source}")

        try:
            # Initialize components
            config_parser = ConfigParser(config)
            crawler = DatabaseCrawler(config_parser)
            dsds_generator = DSDSGenerator(config_parser)

            # Validate configuration
            regex_errors = config_parser.validate_regex_patterns()
            if regex_errors:
                raise ValueError(f"Configuration validation failed: {', '.join(regex_errors)}")

            # Execute crawl
            logger.info("Starting table crawl...")
            crawled_tables = await crawler.crawl_all_tables(db)

            if not crawled_tables:
                raise Exception("No tables were successfully crawled")

            # Generate DSDS
            logger.info("Generating DSDS...")
            enriched_tables = await dsds_generator.generate_dsds_for_tables(db, crawled_tables)

            # Build result
            result = self._build_result(config_parser, enriched_tables)

            # Save to remote file system if requested
            if save_remote:
                await self._save_to_remote_file_system(result)

            logger.info(f"Database crawl completed successfully. Crawled {len(enriched_tables)} tables.")
            return result

        except ValueError as e:
            # Re-raise configuration validation errors as ValueError
            logger.error(f"Configuration validation failed: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Database crawl failed: {str(e)}")
            raise Exception(f"Database crawl operation failed: {str(e)}")

    def _build_result(self, config_parser: ConfigParser, enriched_tables: list) -> DbCrawlResult:
        """Build the final crawl result"""

        # Create metadata
        metadata = RetrievalMetadata(
            timestamp_utc=datetime.now(timezone.utc).isoformat(), source_database=config_parser.get_source_name(), config_hash=config_parser.get_config_hash()
        )

        # Convert table data to result models
        table_results = []
        for table_data in enriched_tables:
            table_result = TableCrawlResult(
                table_name=table_data["table_name"],
                full_path=table_data["full_path"],
                ddl=table_data["ddl"],
                sample_data=table_data["sample_data"],
                dsds=table_data.get("dsds"),
            )
            table_results.append(table_result)

        return DbCrawlResult(retrieval_metadata=metadata, tables=table_results)

    async def _save_to_remote_file_system(self, result: DbCrawlResult) -> None:
        """Save crawled results to remote file system"""
        logger.info("Saving crawled results to remote file system")

        # Create base directory with source database prefix
        source_database = result.retrieval_metadata.source_database
        base_path = settings.RKS_PATH / "system" / source_database
        base_path.mkdir(parents=True, exist_ok=True)

        # Save retrieval metadata
        metadata_path = base_path / ".retrieval_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(result.retrieval_metadata.model_dump(), f, indent=2)

        # Save each table
        for table_result in result.tables:
            table_path = base_path / table_result.table_name
            table_path.mkdir(parents=True, exist_ok=True)

            # Save DDL
            ddl_path = table_path / "ddl.sql"
            with open(ddl_path, "w") as f:
                f.write(table_result.ddl)

            # Save sample data as CSV
            sample_path = table_path / "sample.csv"
            if table_result.sample_data:
                with open(sample_path, "w", newline="") as f:
                    if table_result.sample_data:
                        writer = csv.DictWriter(f, fieldnames=table_result.sample_data[0].keys())
                        writer.writeheader()
                        writer.writerows(table_result.sample_data)

            # Save DSDS
            if table_result.dsds:
                dsds_path = table_path / "dsds.txt"
                with open(dsds_path, "w") as f:
                    f.write(table_result.dsds)

        logger.info(f"Saved {len(result.tables)} tables to remote file system under {source_database}")
