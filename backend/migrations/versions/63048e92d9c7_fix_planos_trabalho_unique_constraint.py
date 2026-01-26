"""fix_planos_trabalho_unique_constraint

Revision ID: 63048e92d9c7
Revises: d58e9f0a1b2c
Create Date: 2026-01-26 08:54:24.293911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63048e92d9c7'
down_revision: Union[str, Sequence[str], None] = 'd58e9f0a1b2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the incorrect global unique constraint
    op.drop_constraint('planos_trabalho_nome_unq', 'planos_trabalho', type_='unique')

    # Create the correct per-empresa unique constraint
    op.create_unique_constraint(
        'planos_trabalho_empresa_nome_unq',
        'planos_trabalho',
        ['empresa_id', 'nome']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Reverse the changes (for rollback capability)
    op.drop_constraint('planos_trabalho_empresa_nome_unq', 'planos_trabalho', type_='unique')

    # Restore the old (incorrect) constraint
    op.create_unique_constraint(
        'planos_trabalho_nome_unq',
        'planos_trabalho',
        ['nome']
    )
