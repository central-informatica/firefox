"""add_usuarios_ip_whitelist_table

Revision ID: b35a6ed3ef8d
Revises: 318b57f47926
Create Date: 2026-01-25 15:14:54.777458

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b35a6ed3ef8d'
down_revision: Union[str, Sequence[str], None] = '318b57f47926'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create usuarios_ip_whitelist table."""
    op.create_table(
        'usuarios_ip_whitelist',
        sa.Column('whitelist_id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('usuario_id', sa.UUID(), nullable=False, comment='ID do usuario (validado pelo Auth service)'),
        sa.Column('empresa_id', sa.UUID(), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('ip_address', sa.String(45), nullable=False, comment='Endereco IP permitido (IPv4 ou IPv6)'),
        sa.Column('descricao', sa.Text(), nullable=True, comment='Descricao opcional para referencia do admin'),
        sa.Column('criado_em', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('criado_por', sa.UUID(), nullable=False, comment='ID do admin que criou a entrada'),
        sa.PrimaryKeyConstraint('whitelist_id', name='usuarios_ip_whitelist_pkey'),
        sa.UniqueConstraint('usuario_id', 'empresa_id', 'ip_address', name='usuarios_ip_whitelist_unq'),
        comment='Lista de IPs permitidos por usuario e empresa.'
    )
    op.create_index('idx_usuarios_ip_whitelist_usuario', 'usuarios_ip_whitelist', ['usuario_id'])
    op.create_index('idx_usuarios_ip_whitelist_empresa', 'usuarios_ip_whitelist', ['empresa_id'])
    op.create_index('idx_usuarios_ip_whitelist_ip', 'usuarios_ip_whitelist', ['ip_address'])


def downgrade() -> None:
    """Drop usuarios_ip_whitelist table."""
    op.drop_index('idx_usuarios_ip_whitelist_ip', table_name='usuarios_ip_whitelist')
    op.drop_index('idx_usuarios_ip_whitelist_empresa', table_name='usuarios_ip_whitelist')
    op.drop_index('idx_usuarios_ip_whitelist_usuario', table_name='usuarios_ip_whitelist')
    op.drop_table('usuarios_ip_whitelist')
