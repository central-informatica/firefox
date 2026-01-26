"""add_soft_delete_to_usuarios_ip_whitelist

Revision ID: c47d8f9e1a2b
Revises: b35a6ed3ef8d
Create Date: 2026-01-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c47d8f9e1a2b'
down_revision: Union[str, Sequence[str], None] = 'b35a6ed3ef8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add soft delete columns to usuarios_ip_whitelist."""
    op.add_column(
        'usuarios_ip_whitelist',
        sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='Data/hora da exclusao (soft delete)')
    )
    op.add_column(
        'usuarios_ip_whitelist',
        sa.Column('deleted_by', sa.UUID(), nullable=True, comment='ID do usuario que excluiu')
    )


def downgrade() -> None:
    """Remove soft delete columns from usuarios_ip_whitelist."""
    op.drop_column('usuarios_ip_whitelist', 'deleted_by')
    op.drop_column('usuarios_ip_whitelist', 'deleted_at')
