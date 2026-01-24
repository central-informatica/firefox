"""add_soft_delete_to_certificados

Revision ID: ab98719ad7d2
Revises: 20608a254021
Create Date: 2026-01-24 10:01:38.408123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'ab98719ad7d2'
down_revision: Union[str, Sequence[str], None] = '20608a254021'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add soft delete columns to certificados table."""
    op.add_column(
        'certificados',
        sa.Column(
            'deleted_at',
            sa.DateTime(),
            nullable=True,
            comment='Data/hora da exclusao (soft delete)'
        )
    )
    op.add_column(
        'certificados',
        sa.Column(
            'deleted_by',
            sa.UUID(),
            nullable=True,
            comment='ID do usuario que excluiu o certificado'
        )
    )


def downgrade() -> None:
    """Remove soft delete columns from certificados table."""
    op.drop_column('certificados', 'deleted_by')
    op.drop_column('certificados', 'deleted_at')
