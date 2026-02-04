"""drop ramos table - categories now come from Auth service

Revision ID: f1a2b3c4d5e6
Revises: e1f2g3h4i5j6
Create Date: 2026-02-04 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = '63048e92d9c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop the ramos table - company categories are now fetched from Auth service."""
    op.drop_table('ramos', if_exists=True)


def downgrade() -> None:
    """Recreate the ramos table."""
    op.create_table(
        'ramos',
        sa.Column('ramos_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('ramo', sa.String(80), nullable=False),
        sa.PrimaryKeyConstraint('ramos_id', name='ramos_pkey'),
        comment='Ramos de atuação das empresas.'
    )
