"""add cofre_cert_id to certificados

Revision ID: 20608a254021
Revises: e1f2g3h4i5j6
Create Date: 2026-01-24 09:42:39.877801

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20608a254021'
down_revision: Union[str, Sequence[str], None] = 'e1f2g3h4i5j6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add cofre_cert_id column to certificados table."""
    op.add_column(
        'certificados',
        sa.Column(
            'cofre_cert_id',
            sa.UUID(),
            nullable=True,
            comment='ID do certificado no servico Cofre'
        )
    )
    # Add index for fast lookups by cofre_cert_id
    op.create_index(
        'idx_cert_cofre',
        'certificados',
        ['cofre_cert_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove cofre_cert_id column from certificados table."""
    op.drop_index('idx_cert_cofre', table_name='certificados')
    op.drop_column('certificados', 'cofre_cert_id')
