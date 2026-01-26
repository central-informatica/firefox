"""add_grupos_certificados_urls_table

Revision ID: d58e9f0a1b2c
Revises: c47d8f9e1a2b
Create Date: 2026-01-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'd58e9f0a1b2c'
down_revision: Union[str, Sequence[str], None] = 'c47d8f9e1a2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create grupos_certificados_urls table."""
    op.create_table(
        'grupos_certificados_urls',
        sa.Column('grupo_cert_url_id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', UUID(), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('grupo_cert_id', UUID(), nullable=False),
        sa.Column('global_urls_id', UUID(), nullable=False),
        sa.PrimaryKeyConstraint('grupo_cert_url_id', name='grupos_certificados_urls_pkey'),
        sa.ForeignKeyConstraint(['grupo_cert_id'], ['grupos_certificados.grupo_cert_id'], ondelete='CASCADE', name='grupos_cert_urls_grupo_cert_fk'),
        sa.ForeignKeyConstraint(['global_urls_id'], ['global_urls.global_urls_id'], ondelete='CASCADE', name='grupos_cert_urls_url_fk'),
        sa.UniqueConstraint('grupo_cert_id', 'global_urls_id', name='grupos_certificados_urls_unq'),
        comment='URLs permitidas para cada relacao grupo-certificado.'
    )
    op.create_index('idx_g_cert_urls_grupo_cert', 'grupos_certificados_urls', ['grupo_cert_id'])
    op.create_index('idx_g_cert_urls_url', 'grupos_certificados_urls', ['global_urls_id'])
    op.create_index('idx_g_cert_urls_emp', 'grupos_certificados_urls', ['empresa_id'])


def downgrade() -> None:
    """Drop grupos_certificados_urls table."""
    op.drop_index('idx_g_cert_urls_emp', table_name='grupos_certificados_urls')
    op.drop_index('idx_g_cert_urls_url', table_name='grupos_certificados_urls')
    op.drop_index('idx_g_cert_urls_grupo_cert', table_name='grupos_certificados_urls')
    op.drop_table('grupos_certificados_urls')
