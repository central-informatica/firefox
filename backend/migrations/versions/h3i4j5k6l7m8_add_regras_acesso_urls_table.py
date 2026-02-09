"""add_regras_acesso_urls_table

Revision ID: h3i4j5k6l7m8
Revises: g2h3i4j5k6l7
Create Date: 2026-02-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = 'h3i4j5k6l7m8'
down_revision: Union[str, Sequence[str], None] = 'g2h3i4j5k6l7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create regras_acesso_urls table."""
    op.create_table(
        'regras_acesso_urls',
        sa.Column('regra_id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', UUID(), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('grupo_id', UUID(), nullable=False),
        sa.Column('global_urls_id', UUID(), nullable=False),
        sa.Column('tipo_dia', sa.String(20), nullable=False, comment='Tipo de regra: corridos, uteis ou especificos.'),
        sa.Column('dias_especificos', sa.ARRAY(sa.Integer()), nullable=True, comment='Lista de dias (ex: 1=segunda ... 7=domingo) quando tipo_dia = especificos.'),
        sa.Column('horarios', JSONB(), nullable=False, comment='Lista de janelas de horario em JSON (inicio/fim no formato HH:MI).'),
        sa.Column('bloquear_em_feriado', sa.Boolean(), nullable=False, server_default=sa.text('false'), comment='Bloqueia acesso em feriados da empresa.'),
        sa.Column('criado_em', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('regra_id', name='regras_acesso_urls_pkey'),
        sa.ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='regras_acesso_urls_grupo_fk'),
        sa.ForeignKeyConstraint(['global_urls_id'], ['global_urls.global_urls_id'], ondelete='CASCADE', name='regras_acesso_urls_url_fk'),
        sa.UniqueConstraint('grupo_id', 'global_urls_id', name='regras_acesso_urls_grupo_url_unq'),
        comment='Regras de dias e horarios permitidos para URLs especificas de um grupo.'
    )
    op.create_index('idx_regras_acesso_urls_grupo', 'regras_acesso_urls', ['grupo_id'])
    op.create_index('idx_regras_acesso_urls_url', 'regras_acesso_urls', ['global_urls_id'])
    op.create_index('idx_regras_acesso_urls_emp', 'regras_acesso_urls', ['empresa_id'])


def downgrade() -> None:
    """Drop regras_acesso_urls table."""
    op.drop_index('idx_regras_acesso_urls_emp', table_name='regras_acesso_urls')
    op.drop_index('idx_regras_acesso_urls_url', table_name='regras_acesso_urls')
    op.drop_index('idx_regras_acesso_urls_grupo', table_name='regras_acesso_urls')
    op.drop_table('regras_acesso_urls')
