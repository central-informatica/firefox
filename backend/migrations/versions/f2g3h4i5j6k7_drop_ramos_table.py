"""drop ramos table

Revision ID: f2g3h4i5j6k7
Revises: e1f2g3h4i5j6
Create Date: 2026-02-09 00:00:00.000000

The ramos table is no longer used by the application.
This migration removes it from the database.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f2g3h4i5j6k7'
down_revision: Union[str, Sequence[str], None] = 'e1f2g3h4i5j6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop the ramos table."""
    op.drop_table('ramos')


def downgrade() -> None:
    """Recreate the ramos table."""
    op.create_table(
        'ramos',
        sa.Column('ramos_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('ramo', sa.String(80), nullable=False),
        sa.PrimaryKeyConstraint('ramos_id', name='ramos_pkey'),
        comment='Ramos de atuacao das empresas.'
    )
