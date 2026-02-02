"""add global_urls table

Revision ID: c1a2b3c4d5e6
Revises: 9a51d7cb501f
Create Date: 2025-12-31 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = '9a51d7cb501f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'global_urls',
        sa.Column('global_urls_id', sa.BigInteger(), nullable=False, comment='Identificador único'),
        sa.Column('url', sa.Text(), nullable=True, comment='URL cadastrada'),
        sa.Column('criado_em', sa.DateTime(), server_default=sa.text('now()'), nullable=True, comment='Data de criação'),
        sa.Column('inativo', sa.Boolean(), server_default=sa.text('false'), nullable=True, comment='Indica se a URL está inativa'),
        sa.Column('empresa_id', sa.BigInteger(), nullable=False, comment='Chave estrangeira da empresa'),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.empresa_id'], name='global_urls_empresa_fk', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('global_urls_id', name='global_urls_pkey'),
        comment='URLs globais cadastradas por empresa.'
    )
    op.create_index('idx_global_urls_emp', 'global_urls', ['empresa_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_global_urls_emp', table_name='global_urls')
    op.drop_table('global_urls')
