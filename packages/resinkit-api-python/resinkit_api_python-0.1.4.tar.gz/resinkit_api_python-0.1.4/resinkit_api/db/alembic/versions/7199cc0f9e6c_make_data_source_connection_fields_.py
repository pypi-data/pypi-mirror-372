"""make data source connection fields nullable for sqlite support

Revision ID: 7199cc0f9e6c
Revises: a261d8461fde
Create Date: 2025-07-21 08:57:54.897078

"""

import enum
import json

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, String, Text, text

from resinkit_api.db.models import JSONString, TaskStatus

# revision identifiers, used by Alembic.
revision = "7199cc0f9e6c"
down_revision = "a261d8461fde"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table

    # Clean up any leftover temp tables from previous failed migrations
    try:
        op.drop_table("data_sources_new")
    except:
        pass  # Table doesn't exist, which is fine

    # Create new table with nullable columns and indexes
    op.create_table(
        "data_sources_new",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("host", sa.String(), nullable=True),  # Now nullable
        sa.Column("port", sa.Integer(), nullable=True),  # Now nullable
        sa.Column("database", sa.String(), nullable=False),
        sa.Column("encrypted_user", sa.String(), nullable=True),  # Now nullable
        sa.Column("encrypted_password", sa.String(), nullable=True),  # Now nullable
        sa.Column("query_timeout", sa.String(), nullable=False, server_default="30s"),
        sa.Column("extra_params", JSONString()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("name"),
        sa.Index("idx_data_sources_new_name", "name"),
        sa.Index("idx_data_sources_new_kind", "kind"),
    )

    # Note: Indexes will be created automatically when we rename the table

    # Copy data from old table to new table
    op.execute("""
        INSERT INTO data_sources_new (name, kind, host, port, database, encrypted_user, encrypted_password, query_timeout, extra_params, created_at, updated_at, created_by)
        SELECT name, kind, host, port, database, encrypted_user, encrypted_password, query_timeout, extra_params, created_at, updated_at, created_by
        FROM data_sources
    """)

    # Drop old table
    op.drop_table("data_sources")

    # Rename new table
    op.rename_table("data_sources_new", "data_sources")


def downgrade() -> None:
    # Reverse the process - recreate with non-nullable columns
    op.create_table(
        "data_sources_old",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("host", sa.String(), nullable=False),  # Back to non-nullable
        sa.Column("port", sa.Integer(), nullable=False),  # Back to non-nullable
        sa.Column("database", sa.String(), nullable=False),
        sa.Column("encrypted_user", sa.String(), nullable=False),  # Back to non-nullable
        sa.Column("encrypted_password", sa.String(), nullable=False),  # Back to non-nullable
        sa.Column("query_timeout", sa.String(), nullable=False, server_default="30s"),
        sa.Column("extra_params", JSONString()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("name"),
        sa.Index("idx_data_sources_old_name", "name"),
        sa.Index("idx_data_sources_old_kind", "kind"),
    )

    # Note: Indexes will be created automatically when we rename the table

    # Copy data back (this may fail if there are null values)
    op.execute("""
        INSERT INTO data_sources_old (name, kind, host, port, database, encrypted_user, encrypted_password, query_timeout, extra_params, created_at, updated_at, created_by)
        SELECT name, kind, 
               COALESCE(host, 'localhost') as host,
               COALESCE(port, 0) as port,
               database,
               COALESCE(encrypted_user, '') as encrypted_user,
               COALESCE(encrypted_password, '') as encrypted_password,
               query_timeout, extra_params, created_at, updated_at, created_by
        FROM data_sources
    """)

    # Drop new table and rename old
    op.drop_table("data_sources")
    op.rename_table("data_sources_old", "data_sources")
