"""Store tracking stage dates without a time component.

Revision ID: b7d31f2c8a40
Revises: aaf2931b1615
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b7d31f2c8a40"
down_revision: Union[str, Sequence[str], None] = "aaf2931b1615"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "project_tracking_stages",
        "date",
        existing_type=sa.DateTime(),
        type_=sa.Date(),
        existing_nullable=True,
        postgresql_using="date::date",
    )


def downgrade() -> None:
    op.alter_column(
        "project_tracking_stages",
        "date",
        existing_type=sa.Date(),
        type_=sa.DateTime(),
        existing_nullable=True,
        postgresql_using="date::timestamp",
    )
