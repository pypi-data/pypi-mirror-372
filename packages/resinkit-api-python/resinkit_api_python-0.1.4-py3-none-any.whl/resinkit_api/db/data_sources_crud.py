from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import update
from sqlalchemy.orm import Session

from resinkit_api.core.logging import get_logger
from resinkit_api.db.models import DataSource
from resinkit_api.db.variables_crud import decrypt_value, encrypt_value, resolve_variables

logger = get_logger(__name__)


async def create_data_source(
    db: Session,
    name: str,
    kind: str,
    host: Optional[str],
    port: Optional[int],
    database: str,
    user: Optional[str],
    password: Optional[str],
    query_timeout: str = "30s",
    extra_params: Optional[Dict] = None,
    created_by: str = "user",
) -> DataSource:
    """Create a new data source with encrypted credentials"""

    # Resolve variables and encrypt credentials only if they are provided
    encrypted_user = None
    encrypted_password = None

    if user is not None:
        resolved_user = await resolve_variables(db, user)
        encrypted_user = encrypt_value(resolved_user)

    if password is not None:
        resolved_password = await resolve_variables(db, password)
        encrypted_password = encrypt_value(resolved_password)

    data_source = DataSource(
        name=name,
        kind=kind,
        host=host,
        port=port,
        database=database,
        encrypted_user=encrypted_user,
        encrypted_password=encrypted_password,
        query_timeout=query_timeout,
        extra_params=extra_params,
        created_by=created_by,
    )

    db.add(data_source)
    db.commit()
    db.refresh(data_source)

    logger.info(f"Created data source: {name}")
    return data_source


async def get_data_source(db: Session, name: str) -> Optional[DataSource]:
    """Get a data source by name"""
    return db.query(DataSource).filter(DataSource.name == name).first()


async def list_data_sources(db: Session) -> List[DataSource]:
    """List all data sources"""
    return db.query(DataSource).all()


async def update_data_source(
    db: Session,
    name: str,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    query_timeout: Optional[str] = None,
    extra_params: Optional[Dict] = None,
) -> Optional[DataSource]:
    """Update a data source"""

    data_source = await get_data_source(db, name)
    if not data_source:
        return None

    update_data = {"updated_at": datetime.utcnow()}

    if host is not None:
        update_data["host"] = host
    if port is not None:
        update_data["port"] = port
    if database is not None:
        update_data["database"] = database
    if user is not None:
        resolved_user = await resolve_variables(db, user)
        update_data["encrypted_user"] = encrypt_value(resolved_user)
    if password is not None:
        resolved_password = await resolve_variables(db, password)
        update_data["encrypted_password"] = encrypt_value(resolved_password)
    if query_timeout is not None:
        update_data["query_timeout"] = query_timeout
    if extra_params is not None:
        update_data["extra_params"] = extra_params

    db.execute(update(DataSource).where(DataSource.name == name).values(**update_data))
    db.commit()

    # Refresh and return updated source
    db.refresh(data_source)
    logger.info(f"Updated data source: {name}")
    return data_source


async def delete_data_source(db: Session, name: str) -> bool:
    """Delete a data source"""
    data_source = await get_data_source(db, name)
    if not data_source:
        return False

    db.delete(data_source)
    db.commit()

    logger.info(f"Deleted data source: {name}")
    return True


async def get_decrypted_credentials(db: Session, name: str) -> Optional[Dict[str, str]]:
    """Get decrypted credentials for a data source"""
    data_source = await get_data_source(db, name)
    if not data_source:
        return None

    try:
        result = {}

        if data_source.encrypted_user is not None:
            result["user"] = decrypt_value(data_source.encrypted_user)

        if data_source.encrypted_password is not None:
            result["password"] = decrypt_value(data_source.encrypted_password)

        return result
    except Exception as e:
        logger.error(f"Failed to decrypt credentials for data source {name}: {str(e)}")
        return None


# Backwards compatibility aliases
create_sql_source = create_data_source
get_sql_source = get_data_source
list_sql_sources = list_data_sources
update_sql_source = update_data_source
delete_sql_source = delete_data_source
