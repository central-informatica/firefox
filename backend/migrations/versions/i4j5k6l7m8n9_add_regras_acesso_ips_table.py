"""add_regras_acesso_ips_table

Revision ID: i4j5k6l7m8n9
Revises: h3i4j5k6l7m8
Create Date: 2026-02-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB


# revision identifiers, used by Alembic.
revision: str = 'i4j5k6l7m8n9'
down_revision: Union[str, Sequence[str], None] = 'h3i4j5k6l7m8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create regras_acesso_ips table."""
    op.create_table(
        'regras_acesso_ips',
        sa.Column('regra_id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', UUID(), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('grupo_id', UUID(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=False, comment='Endereco IP (IPv4 ou IPv6)'),
        sa.Column('tipo_dia', sa.String(20), nullable=False, comment='Tipo de regra: corridos, uteis ou especificos.'),
        sa.Column('dias_especificos', sa.ARRAY(sa.Integer()), nullable=True, comment='Lista de dias (ex: 1=segunda ... 7=domingo) quando tipo_dia = especificos.'),
        sa.Column('horarios', JSONB(), nullable=False, comment='Lista de janelas de horario em JSON (inicio/fim no formato HH:MI).'),
        sa.Column('bloquear_em_feriado', sa.Boolean(), nullable=False, server_default=sa.text('false'), comment='Bloqueia acesso em feriados da empresa.'),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default=sa.text('true'), comment='Indica se a regra esta ativa.'),
        sa.Column('criado_em', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('regra_id', name='regras_acesso_ips_pkey'),
        sa.ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], ondelete='CASCADE', name='regras_acesso_ips_grupo_fk'),
        sa.UniqueConstraint('grupo_id', 'ip_address', name='regras_acesso_ips_grupo_ip_unq'),
        comment='Regras de dias e horarios permitidos para enderecos IP especificos de um grupo.'
    )
    op.create_index('idx_regras_acesso_ips_grupo', 'regras_acesso_ips', ['grupo_id'])
    op.create_index('idx_regras_acesso_ips_ip', 'regras_acesso_ips', ['ip_address'])
    op.create_index('idx_regras_acesso_ips_emp', 'regras_acesso_ips', ['empresa_id'])


def downgrade() -> None:
    """Drop regras_acesso_ips table."""
    op.drop_index('idx_regras_acesso_ips_emp', table_name='regras_acesso_ips')
    op.drop_index('idx_regras_acesso_ips_ip', table_name='regras_acesso_ips')
    op.drop_index('idx_regras_acesso_ips_grupo', table_name='regras_acesso_ips')
    op.drop_table('regras_acesso_ips')
