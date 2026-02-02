"""convert bigint to uuid and remove auth-managed tables

Revision ID: e1f2g3h4i5j6
Revises: d1e2f3a4b5c6
Create Date: 2026-01-23 18:00:00.000000

WARNING: This migration will DROP all data. Only run on empty/new databases.

Note: The following tables are now managed by the Auth microservice and are NOT created here:
- usuarios
- empresas
- empresa_membros
- empresa_convites
- access_tokens

The empresa_id, usuario_id, and criado_por columns are kept for multi-tenant data isolation,
but without FK constraints since Auth service validates these IDs externally.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e1f2g3h4i5j6'
down_revision: Union[str, Sequence[str], None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Convert all BIGINT primary and foreign keys to UUID.
    Remove Auth-managed tables (usuarios, empresas, etc.).

    WARNING: This drops all existing data. Only run on empty/new databases.
    """
    # Drop all tables in correct order (respecting foreign keys)
    op.drop_table('grupos_certificados', if_exists=True)
    op.drop_table('grupos_usuarios', if_exists=True)
    op.drop_table('regras_acesso', if_exists=True)
    op.drop_table('regras_acesso_hosts', if_exists=True)
    op.drop_table('global_urls', if_exists=True)
    op.drop_table('feriados', if_exists=True)
    op.drop_table('grupos', if_exists=True)
    op.drop_table('planos_trabalho', if_exists=True)
    op.drop_table('certificados', if_exists=True)
    op.drop_table('empresa_convites', if_exists=True)
    op.drop_table('empresa_membros', if_exists=True)
    op.drop_table('empresas', if_exists=True)
    op.drop_table('access_tokens', if_exists=True)
    op.drop_table('usuarios', if_exists=True)
    op.drop_table('ramos', if_exists=True)

    # Recreate tables with UUID columns
    # NOTE: Auth-managed tables (usuarios, empresas, empresa_membros, empresa_convites, access_tokens)
    # are NOT created here - they are managed by the Auth microservice.

    # ramos - standalone reference data
    op.create_table(
        'ramos',
        sa.Column('ramos_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('ramo', sa.String(80), nullable=False),
        sa.PrimaryKeyConstraint('ramos_id', name='ramos_pkey'),
        comment='Ramos de atuação das empresas.'
    )

    # certificados - NO FK to empresas or usuarios (Auth-managed)
    op.create_table(
        'certificados',
        sa.Column('certificado_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('criado_por', postgresql.UUID(as_uuid=True), nullable=False, comment='ID do usuario que criou (validado pelo Auth service)'),
        sa.Column('nome_arquivo', sa.Text(), nullable=False, comment='Nome original do arquivo de certificado.'),
        sa.Column('encrypted', sa.Text(), nullable=False, comment='Dados do certificado em formato criptografado.'),
        sa.Column('secret', sa.Text(), nullable=False, comment='Frase secreta ou chave auxiliar usada na criptografia.'),
        sa.Column('criado_em', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('proprietario', sa.String(), nullable=True, comment='Proprietario do certificado'),
        sa.Column('emitido_por', sa.String(), nullable=True, comment='Nome da entidade emissora do certificado'),
        sa.Column('validade_inicio', sa.TIMESTAMP(timezone=True), nullable=True, comment='Data de inicio da validade'),
        sa.Column('valido_ate', sa.TIMESTAMP(timezone=True), nullable=True, comment='Data do fim da validade'),
        sa.PrimaryKeyConstraint('certificado_id', name='certificados_pkey'),
        comment='Certificados digitais criptografados das empresas.'
    )
    op.create_index('idx_cert_emp', 'certificados', ['empresa_id'])
    op.create_index('idx_cert_criado_por', 'certificados', ['criado_por'])

    # feriados - NO FK to empresas (Auth-managed)
    op.create_table(
        'feriados',
        sa.Column('feriado_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('data', sa.Date(), nullable=False),
        sa.Column('nome', sa.String(120), nullable=False),
        sa.Column('recorrente', sa.Boolean(), server_default=sa.text('false'), nullable=False, comment='Indica se o feriado se repete todos os anos na mesma data.'),
        sa.Column('criado_em', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('feriado_id', name='feriados_pkey'),
        comment='Feriados cadastrados por empresa, usados para bloquear acessos.'
    )
    op.create_index('idx_feriados_emp', 'feriados', ['empresa_id'])

    # planos_trabalho - NO FK to empresas (Auth-managed)
    op.create_table(
        'planos_trabalho',
        sa.Column('plano_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('nome', sa.String(100), nullable=False, comment='Nome do plano de trabalho (deve ser unico dentro da empresa).'),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('criado_em', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('plano_id', name='planos_trabalho_pkey'),
        sa.UniqueConstraint('nome', name='planos_trabalho_nome_unq'),
        comment='Planos de trabalho de uma empresa (modelos de regras e grupos).'
    )
    op.create_index('idx_planos_trabalho_emp', 'planos_trabalho', ['empresa_id'])

    # grupos - FK to planos_trabalho only, NO FK to empresas (Auth-managed)
    op.create_table(
        'grupos',
        sa.Column('grupo_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('plano_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nome', sa.String(100), nullable=False, comment='Nome do grupo (unico dentro da empresa).'),
        sa.Column('criado_em', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['plano_id'], ['planos_trabalho.plano_id'], name='grupos_plano_fk', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('grupo_id', name='grupos_pkey'),
        sa.UniqueConstraint('empresa_id', 'nome', name='grupos_empresa_nome_unq'),
        comment='Grupos de usuarios pertencentes a planos de trabalho de uma empresa.'
    )
    op.create_index('idx_grupos_emp', 'grupos', ['empresa_id'])
    op.create_index('idx_grupos_plano', 'grupos', ['plano_id'])

    # grupos_certificados - FK to grupos and certificados only, NO FK to empresas
    op.create_table(
        'grupos_certificados',
        sa.Column('grupo_cert_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('grupo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('certificado_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], name='grupos_certificados_grupo_fk', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['certificado_id'], ['certificados.certificado_id'], name='grupos_certificados_cert_fk', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('grupo_cert_id', name='grupos_certificados_pkey'),
        sa.UniqueConstraint('grupo_id', 'certificado_id', name='grupos_certificados_unq'),
        comment='Relacao de quais certificados cada grupo pode acessar.'
    )
    op.create_index('idx_g_cert_grupo', 'grupos_certificados', ['grupo_id'])
    op.create_index('idx_g_cert_cert', 'grupos_certificados', ['certificado_id'])
    op.create_index('idx_g_cert_emp', 'grupos_certificados', ['empresa_id'])

    # grupos_usuarios - FK to grupos only, NO FK to empresas or usuarios (Auth-managed)
    op.create_table(
        'grupos_usuarios',
        sa.Column('grupo_usuario_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('grupo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('usuario_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID do usuario (validado pelo Auth service)'),
        sa.ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], name='grupos_usuarios_grupo_fk', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('grupo_usuario_id', name='grupos_usuarios_pkey'),
        sa.UniqueConstraint('grupo_id', 'usuario_id', name='grupos_usuarios_unq'),
        comment='Relacao entre usuarios e grupos, dentro de uma empresa.'
    )
    op.create_index('idx_g_usuarios_grupo', 'grupos_usuarios', ['grupo_id'])
    op.create_index('idx_g_usuarios_user', 'grupos_usuarios', ['usuario_id'])
    op.create_index('idx_g_usuarios_emp', 'grupos_usuarios', ['empresa_id'])

    # regras_acesso - FK to grupos only, NO FK to empresas (Auth-managed)
    op.create_table(
        'regras_acesso',
        sa.Column('regra_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('grupo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_dia', sa.String(20), nullable=False, comment='Tipo de regra: corridos, uteis ou especificos.'),
        sa.Column('dias_especificos', postgresql.ARRAY(sa.Integer()), nullable=True, comment='Lista de dias (ex: 1=segunda ... 7=domingo) quando tipo_dia = especificos.'),
        sa.Column('horarios', postgresql.JSONB(), nullable=False, comment='Lista de janelas de horario em JSON (inicio/fim no formato HH:MI).'),
        sa.Column('criado_em', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], name='regras_grupo_fk', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('regra_id', name='regras_acesso_pkey'),
        comment='Regras de dias e horarios permitidos para grupos de uma empresa.'
    )
    op.create_index('idx_regras_grupo', 'regras_acesso', ['grupo_id'])
    op.create_index('idx_regras_emp', 'regras_acesso', ['empresa_id'])

    # regras_acesso_hosts - FK to grupos only, NO FK to empresas (Auth-managed)
    op.create_table(
        'regras_acesso_hosts',
        sa.Column('regra_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('grupo_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tipo_dia', sa.String(20), nullable=False),
        sa.Column('dias_especificos', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('horarios', postgresql.JSONB(), nullable=False),
        sa.Column('urls', sa.Text(), nullable=True),
        sa.Column('criado_em', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['grupo_id'], ['grupos.grupo_id'], name='regras_hosts_grupo_fk', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('regra_id', name='regras_acesso_hosts_pkey'),
    )
    op.create_index('idx_regras_acesso_hosts_grupo', 'regras_acesso_hosts', ['grupo_id'])
    op.create_index('idx_regras_hosts_emp', 'regras_acesso_hosts', ['empresa_id'])

    # global_urls - NO FK to empresas (Auth-managed)
    op.create_table(
        'global_urls',
        sa.Column('global_urls_id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False, comment='Identificador unico'),
        sa.Column('empresa_id', postgresql.UUID(as_uuid=True), nullable=False, comment='ID da empresa (validado pelo Auth service)'),
        sa.Column('url', sa.Text(), nullable=True, comment='URL cadastrada'),
        sa.Column('criado_em', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True, comment='Data de criacao'),
        sa.Column('inativo', sa.Boolean(), server_default=sa.text('false'), nullable=True, comment='Indica se a URL esta inativa'),
        sa.PrimaryKeyConstraint('global_urls_id', name='global_urls_pkey'),
        comment='URLs globais cadastradas por empresa.'
    )
    op.create_index('idx_global_urls_emp', 'global_urls', ['empresa_id'])


def downgrade() -> None:
    """
    This migration cannot be safely downgraded as it destroys data.
    To rollback, restore from backup.
    """
    raise NotImplementedError(
        "Cannot downgrade from UUID to BIGINT migration. Restore from backup."
    )
