"""add ativo field to certificados

Revision ID: g2h3i4j5k6l7
Revises: f1a2b3c4d5e6
Create Date: 2026-02-05 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g2h3i4j5k6l7'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ativo column to certificados table."""
    op.add_column(
        'certificados',
        sa.Column(
            'ativo',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
            comment='Indica se o certificado esta ativo para uso'
        )
    )


def downgrade() -> None:
    """Remove ativo column from certificados table."""
    op.drop_column('certificados', 'ativo')
