from resinkit_api.services.agent.data_sources_service import DataSourceService


def get_data_source_service() -> DataSourceService:
    """Dependency to get DataSourceService instance"""
    return DataSourceService()
