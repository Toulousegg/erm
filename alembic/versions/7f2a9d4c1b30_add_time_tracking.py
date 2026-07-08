"""add time tracking

Revision ID: 7f2a9d4c1b30
Revises: 016f6d5b21ca
Create Date: 2026-06-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7f2a9d4c1b30'
down_revision: Union[str, Sequence[str], None] = '016f6d5b21ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PROJECT_STAGE_VALUES = (
    'planning',
    'cutting',
    'pre_assembly',
    'lamination',
    'truck_loading',
    'installation',
    'finishing',
    'correction',
    'other',
)


def upgrade() -> None:
    """Upgrade schema."""
    project_stage_enum = postgresql.ENUM(*PROJECT_STAGE_VALUES, name='projectstageenum')
    table_stage_enum = postgresql.ENUM(*PROJECT_STAGE_VALUES, name='projectstageenum', create_type=False)

    project_stage_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'time_entries',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('stage', table_stage_enum, nullable=False),
        sa.Column('task', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('work_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.Time(), nullable=False),
        sa.Column('end_time', sa.Time(), nullable=False),
        sa.Column('total_minutes', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['employee_id'], ['users.id']),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(op.f('ix_time_entries_id'), 'time_entries', ['id'], unique=False)
    op.create_index(op.f('ix_time_entries_employee_id'), 'time_entries', ['employee_id'], unique=False)
    op.create_index(op.f('ix_time_entries_company_id'), 'time_entries', ['company_id'], unique=False)
    op.create_index(op.f('ix_time_entries_project_id'), 'time_entries', ['project_id'], unique=False)
    op.create_index(op.f('ix_time_entries_stage'), 'time_entries', ['stage'], unique=False)
    op.create_index(op.f('ix_time_entries_task'), 'time_entries', ['task'], unique=False)
    op.create_index(op.f('ix_time_entries_work_date'), 'time_entries', ['work_date'], unique=False)
    op.create_index(op.f('ix_time_entries_total_minutes'), 'time_entries', ['total_minutes'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_time_entries_total_minutes'), table_name='time_entries')
    op.drop_index(op.f('ix_time_entries_work_date'), table_name='time_entries')
    op.drop_index(op.f('ix_time_entries_task'), table_name='time_entries')
    op.drop_index(op.f('ix_time_entries_stage'), table_name='time_entries')
    op.drop_index(op.f('ix_time_entries_project_id'), table_name='time_entries')
    op.drop_index(op.f('ix_time_entries_company_id'), table_name='time_entries')
    op.drop_index(op.f('ix_time_entries_employee_id'), table_name='time_entries')
    op.drop_index(op.f('ix_time_entries_id'), table_name='time_entries')
    op.drop_table('time_entries')
    project_stage_enum = postgresql.ENUM(*PROJECT_STAGE_VALUES, name='projectstageenum')
    project_stage_enum.drop(op.get_bind(), checkfirst=True)
