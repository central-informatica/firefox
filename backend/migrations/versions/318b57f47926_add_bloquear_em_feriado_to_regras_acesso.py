"""add bloquear_em_feriado to regras_acesso

Revision ID: 318b57f47926
Revises: ab98719ad7d2
Create Date: 2026-01-24 10:44:30.737235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '318b57f47926'
down_revision: Union[str, Sequence[str], None] = 'ab98719ad7d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add bloquear_em_feriado column to regras_acesso and regras_acesso_hosts tables."""
    op.add_column(
        'regras_acesso',
        sa.Column(
            'bloquear_em_feriado',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
            comment='Bloqueia acesso em feriados da empresa.'
        )
    )
    op.add_column(
        'regras_acesso_hosts',
        sa.Column(
            'bloquear_em_feriado',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false'),
            comment='Bloqueia acesso em feriados da empresa.'
        )
    )


def downgrade() -> None:
    """Remove bloquear_em_feriado column from regras_acesso and regras_acesso_hosts tables."""
    op.drop_column('regras_acesso_hosts', 'bloquear_em_feriado')
    op.drop_column('regras_acesso', 'bloquear_em_feriado')
