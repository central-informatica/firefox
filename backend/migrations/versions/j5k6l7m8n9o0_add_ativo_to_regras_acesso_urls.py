"""add_ativo_to_regras_acesso_urls

Revision ID: j5k6l7m8n9o0
Revises: i4j5k6l7m8n9
Create Date: 2026-02-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'j5k6l7m8n9o0'
down_revision: Union[str, Sequence[str], None] = 'i4j5k6l7m8n9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add ativo column to regras_acesso_urls table."""
    op.add_column(
        'regras_acesso_urls',
        sa.Column(
            'ativo',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('true'),
            comment='Indica se a regra esta ativa.'
        )
    )


def downgrade() -> None:
    """Remove ativo column from regras_acesso_urls table."""
    op.drop_column('regras_acesso_urls', 'ativo')
