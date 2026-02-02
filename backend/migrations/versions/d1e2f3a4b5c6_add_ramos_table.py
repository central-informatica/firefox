"""add ramos table and FK to empresas

Revision ID: d1e2f3a4b5c6
Revises: c1a2b3c4d5e6
Create Date: 2025-12-31 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, Sequence[str], None] = 'c1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Criar tabela ramos
    op.create_table(
        'ramos',
        sa.Column('ramos_id', sa.BigInteger(), nullable=False),
        sa.Column('ramo', sa.String(80), nullable=False, comment='Nome do ramo de atuação.'),
        sa.PrimaryKeyConstraint('ramos_id', name='ramos_pkey'),
        comment='Ramos de atuação das empresas.'
    )

    # Inserir registro padrão "Não informado"
    op.execute("INSERT INTO ramos (ramos_id, ramo) VALUES (1, 'Não informado')")

    # Adicionar coluna ramos_id na tabela empresas com valor padrão 1
    op.add_column(
        'empresas',
        sa.Column('ramos_id', sa.BigInteger(), nullable=False, server_default='1', comment='Ramo de atuação da empresa.')
    )

    # Criar FK de empresas para ramos
    op.create_foreign_key(
        'empresas_ramos_fk',
        'empresas',
        'ramos',
        ['ramos_id'],
        ['ramos_id'],
        ondelete='RESTRICT',
        onupdate='CASCADE'
    )

    # Criar índice para ramos_id em empresas
    op.create_index('idx_empresas_ramos', 'empresas', ['ramos_id'], unique=False)


def downgrade() -> None:
    # Remover índice
    op.drop_index('idx_empresas_ramos', table_name='empresas')

    # Remover FK
    op.drop_constraint('empresas_ramos_fk', 'empresas', type_='foreignkey')

    # Remover coluna ramos_id de empresas
    op.drop_column('empresas', 'ramos_id')

    # Remover tabela ramos
    op.drop_table('ramos')
