"""subscription modules

Revision ID: 8d0f0d5c4f21
Revises: 661387e5497e
Create Date: 2026-07-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8d0f0d5c4f21"
down_revision: Union[str, Sequence[str], None] = "661387e5497e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE subscriptionstatusenum ADD VALUE IF NOT EXISTS 'ACTIVE'")
    op.execute("ALTER TYPE subscriptionstatusenum ADD VALUE IF NOT EXISTS 'PAST_DUE'")
    op.execute("ALTER TYPE subscriptionstatusenum ADD VALUE IF NOT EXISTS 'CANCELED'")
    op.add_column("subscription", sa.Column("moduls", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("subscription", "moduls")
