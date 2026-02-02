"""initial schema

Revision ID: 2a3106605800
Revises:
Create Date: 2025-12-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2a3106605800'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # --------------------------
    # EXTENSIONS
    # --------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # --------------------------
    # ENUM TYPES
    # --------------------------
    # Removido: o ENUM já é criado automaticamente pelo SQLAlchemy 
    # Mantemos apenas um guard-routine caso queira adicionar no futuro:
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_type WHERE typname = 'usuario_nivel'
        ) THEN
            CREATE TYPE usuario_nivel AS ENUM ('ADMINISTRADOR', 'COMUM');
        END IF;
    END$$;
    """)

    # --------------------------
    # SEQUENCES
    # --------------------------
    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS usuarios_usuario_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS empresas_empresa_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS empresa_membros_membro_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS empresa_convites_convite_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS certificados_certificado_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS feriados_feriado_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS planos_trabalho_plano_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS grupos_grupo_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS grupos_usuarios_grupo_usuario_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS grupos_certificados_grupo_cert_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS regras_acesso_regra_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS regras_acesso_hosts_regra_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    op.execute("""
        CREATE SEQUENCE IF NOT EXISTS acesso_acesso_id_seq
        INCREMENT BY 1 MINVALUE 1 START WITH 1
    """)

    # --------------------------
    # TABLE: usuarios
    # --------------------------
    op.create_table(
        "usuarios",
        sa.Column("usuario_id", sa.BigInteger(), server_default=sa.text("nextval('usuarios_usuario_id_seq')"), nullable=False),
        sa.Column("nome", sa.String(80), nullable=False),
        sa.Column("email", sa.String(150), nullable=False),
        sa.Column("telefone", sa.String(40)),
        sa.Column("senha_hash", sa.Text(), nullable=False),
        sa.Column("email_verificado", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("atualizado_em", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("nivel", sa.String(20), nullable=False, server_default="'COMUM'"),
        sa.PrimaryKeyConstraint("usuario_id"),
        sa.UniqueConstraint("email")
    )

    # --------------------------
    # TABLE: empresas
    # --------------------------
    op.create_table(
        "empresas",
        sa.Column("empresa_id", sa.BigInteger(), server_default=sa.text("nextval('empresas_empresa_id_seq')"), nullable=False),
        sa.Column("razao_social", sa.String(120), nullable=False),
        sa.Column("fantasia", sa.String(120)),
        sa.Column("cnpj", sa.String(14), nullable=False),
        sa.Column("anfitria_usuario_id", sa.BigInteger(), nullable=False),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="'America/Sao_Paulo'"),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("empresa_id"),
        sa.UniqueConstraint("cnpj")
    )

    # --------------------------
    # TABLE: empresa_membros
    # --------------------------
    op.create_table(
        "empresa_membros",
        sa.Column("membro_id", sa.BigInteger(), server_default=sa.text("nextval('empresa_membros_membro_id_seq')"), nullable=False),
        sa.Column("empresa_id", sa.BigInteger(), nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        sa.Column("papel", sa.String(20), nullable=False, server_default="'COMUM'"),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("membro_id"),
        sa.UniqueConstraint("empresa_id", "usuario_id")
    )

    # --------------------------
    # TABLE: empresa_convites
    # --------------------------
    op.create_table(
        "empresa_convites",
        sa.Column("convite_id", sa.BigInteger(), server_default=sa.text("nextval('empresa_convites_convite_id_seq')"), nullable=False),
        sa.Column("empresa_id", sa.BigInteger(), nullable=False),
        sa.Column("email_convidado", sa.String(150), nullable=False),
        sa.Column("convidado_usuario_id", sa.BigInteger()),
        sa.Column("status", sa.String(20), nullable=False, server_default="'pendente'"),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("convite_uuid", postgresql.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("expiracao", sa.TIMESTAMP(), server_default=sa.text("now() + interval '7 days'")),
        sa.PrimaryKeyConstraint("convite_id"),
        sa.UniqueConstraint("convite_uuid")
    )

    # --------------------------
    # TABLE: certificados
    # --------------------------
    op.create_table(
        "certificados",
        sa.Column("certificado_id", sa.BigInteger(), server_default=sa.text("nextval('certificados_certificado_id_seq')"), nullable=False),
        sa.Column("empresa_id", sa.BigInteger(), nullable=False),
        sa.Column("criado_por", sa.BigInteger(), nullable=False),
        sa.Column("nome_arquivo", sa.Text(), nullable=False),
        sa.Column("encrypted", sa.Text(), nullable=False),
        sa.Column("secret", sa.Text(), nullable=False),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("proprietario", sa.String()),
        sa.Column("emitido_por", sa.String()),
        sa.Column("validade_inicio", sa.TIMESTAMP(timezone=True)),
        sa.Column("valido_ate", sa.TIMESTAMP(timezone=True)),
        sa.PrimaryKeyConstraint("certificado_id")
    )

    # --------------------------
    # TABLE: feriados
    # --------------------------
    op.create_table(
        "feriados",
        sa.Column("feriado_id", sa.BigInteger(), server_default=sa.text("nextval('feriados_feriado_id_seq')"), nullable=False),
        sa.Column("empresa_id", sa.BigInteger(), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("recorrente", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("feriado_id")
    )

    # --------------------------
    # TABLE: planos_trabalho
    # --------------------------
    op.create_table(
        "planos_trabalho",
        sa.Column("plano_id", sa.BigInteger(), server_default=sa.text("nextval('planos_trabalho_plano_id_seq')"), nullable=False),
        sa.Column("empresa_id", sa.BigInteger(), nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("descricao", sa.Text()),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("plano_id"),
        sa.UniqueConstraint("empresa_id", "nome")
    )

    # --------------------------
    # TABLE: grupos
    # --------------------------
    op.create_table(
        "grupos",
        sa.Column("grupo_id", sa.BigInteger(), server_default=sa.text("nextval('grupos_grupo_id_seq')"), nullable=False),
        sa.Column("empresa_id", sa.BigInteger(), nullable=False),
        sa.Column("plano_id", sa.BigInteger(), nullable=False),
        sa.Column("nome", sa.String(100), nullable=False),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("grupo_id"),
        sa.UniqueConstraint("empresa_id", "nome")
    )

    # --------------------------
    # TABLE: grupos_usuarios
    # --------------------------
    op.create_table(
        "grupos_usuarios",
        sa.Column("grupo_usuario_id", sa.BigInteger(), server_default=sa.text("nextval('grupos_usuarios_grupo_usuario_id_seq')"), nullable=False),
        sa.Column("empresa_id", sa.BigInteger(), nullable=False),
        sa.Column("grupo_id", sa.BigInteger(), nullable=False),
        sa.Column("usuario_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("grupo_usuario_id"),
        sa.UniqueConstraint("grupo_id", "usuario_id")
    )

    # --------------------------
    # TABLE: grupos_certificados
    # --------------------------
    op.create_table(
        "grupos_certificados",
        sa.Column("grupo_cert_id", sa.BigInteger(), server_default=sa.text("nextval('grupos_certificados_grupo_cert_id_seq')"), nullable=False),
        sa.Column("empresa_id", sa.BigInteger(), nullable=False),
        sa.Column("grupo_id", sa.BigInteger(), nullable=False),
        sa.Column("certificado_id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("grupo_cert_id"),
        sa.UniqueConstraint("grupo_id", "certificado_id")
    )

    # --------------------------
    # TABLE: regras_acesso
    # --------------------------
    op.create_table(
        "regras_acesso",
        sa.Column("regra_id", sa.BigInteger(), server_default=sa.text("nextval('regras_acesso_regra_id_seq')"), nullable=False),
        sa.Column("empresa_id", sa.BigInteger(), nullable=False),
        sa.Column("grupo_id", sa.BigInteger(), nullable=False),
        sa.Column("tipo_dia", sa.String(20), nullable=False),
        sa.Column("dias_especificos", sa.ARRAY(sa.Integer())),
        sa.Column("horarios", sa.JSON(), nullable=False),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("bloquear_em_feriado", sa.Boolean(), server_default="false"),
        sa.PrimaryKeyConstraint("regra_id")
    )

    # --------------------------
    # TABLE: regras_acesso_hosts
    # --------------------------
    op.create_table(
        "regras_acesso_hosts",
        sa.Column("regra_id", sa.BigInteger(), server_default=sa.text("nextval('regras_acesso_hosts_regra_id_seq')"), nullable=False),
        sa.Column("empresa_id", sa.BigInteger(), nullable=False),
        sa.Column("grupo_id", sa.BigInteger(), nullable=False),
        sa.Column("tipo_dia", sa.String(20), nullable=False),
        sa.Column("dias_especificos", sa.ARRAY(sa.Integer())),
        sa.Column("horarios", sa.JSON(), nullable=False),
        sa.Column("urls", sa.Text()),
        sa.Column("criado_em", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=False),
        sa.Column("bloquear_em_feriado", sa.Boolean(), server_default="false"),
        sa.PrimaryKeyConstraint("regra_id")
    )

    # --------------------------
    # TABLE: acesso
    # --------------------------
    op.create_table(
        "acesso",
        sa.Column("acesso_id", sa.BigInteger(), server_default=sa.text("nextval('acesso_acesso_id_seq')"), nullable=False),
        sa.Column("id_usuario", sa.BigInteger(), nullable=False),
        sa.Column("token", sa.String(255), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("criado_em", sa.TIMESTAMP(), nullable=False, server_default=sa.text("now()")),
        sa.Column("expira_em", sa.TIMESTAMP(), nullable=False, server_default=sa.text("now() + interval '7 days'")),
        sa.PrimaryKeyConstraint("acesso_id"),
        sa.UniqueConstraint("token")
    )

    # --------------------------
    # FOREIGN KEYS
    # --------------------------

    # empresas → usuarios
    op.create_foreign_key(
        "fk_empresas_usuario",
        "empresas", "usuarios",
        ["anfitria_usuario_id"], ["usuario_id"],
        ondelete="CASCADE"
    )

    # empresa_membros → empresas / usuarios
    op.create_foreign_key(
        "fk_membros_empresa",
        "empresa_membros", "empresas",
        ["empresa_id"], ["empresa_id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_membros_usuario",
        "empresa_membros", "usuarios",
        ["usuario_id"], ["usuario_id"],
        ondelete="CASCADE"
    )

    # empresa_convites → empresas / usuarios
    op.create_foreign_key(
        "fk_convites_empresa",
        "empresa_convites", "empresas",
        ["empresa_id"], ["empresa_id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_convites_usuario",
        "empresa_convites", "usuarios",
        ["convidado_usuario_id"], ["usuario_id"],
        ondelete="SET NULL"
    )

    # certificados → empresas / usuarios
    op.create_foreign_key(
        "fk_cert_emp",
        "certificados", "empresas",
        ["empresa_id"], ["empresa_id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_cert_user",
        "certificados", "usuarios",
        ["criado_por"], ["usuario_id"],
        ondelete="CASCADE"
    )

    # feriados → empresas
    op.create_foreign_key(
        "fk_feriados_emp",
        "feriados", "empresas",
        ["empresa_id"], ["empresa_id"],
        ondelete="CASCADE"
    )

    # planos_trabalho → empresas
    op.create_foreign_key(
        "fk_planos_emp",
        "planos_trabalho", "empresas",
        ["empresa_id"], ["empresa_id"],
        ondelete="CASCADE"
    )

    # grupos → planos_trabalho / empresas
    op.create_foreign_key(
        "fk_grupos_emp",
        "grupos", "empresas",
        ["empresa_id"], ["empresa_id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_grupos_plano",
        "grupos", "planos_trabalho",
        ["plano_id"], ["plano_id"],
        ondelete="CASCADE"
    )

    # grupos_usuarios → grupos / usuarios / empresas
    op.create_foreign_key(
        "fk_gusuarios_emp",
        "grupos_usuarios", "empresas",
        ["empresa_id"], ["empresa_id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_gusuarios_grupo",
        "grupos_usuarios", "grupos",
        ["grupo_id"], ["grupo_id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_gusuarios_usuario",
        "grupos_usuarios", "usuarios",
        ["usuario_id"], ["usuario_id"],
        ondelete="CASCADE"
    )

    # grupos_certificados → grupos / certificados / empresas
    op.create_foreign_key(
        "fk_gcert_emp",
        "grupos_certificados", "empresas",
        ["empresa_id"], ["empresa_id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_gcert_grupo",
        "grupos_certificados", "grupos",
        ["grupo_id"], ["grupo_id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_gcert_cert",
        "grupos_certificados", "certificados",
        ["certificado_id"], ["certificado_id"],
        ondelete="CASCADE"
    )

    # regras_acesso → empresas / grupos
    op.create_foreign_key(
        "fk_regras_emp",
        "regras_acesso", "empresas",
        ["empresa_id"], ["empresa_id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_regras_grupo",
        "regras_acesso", "grupos",
        ["grupo_id"], ["grupo_id"],
        ondelete="CASCADE"
    )

    # regras_acesso_hosts → empresas / grupos
    op.create_foreign_key(
        "fk_regras_hosts_emp",
        "regras_acesso_hosts", "empresas",
        ["empresa_id"], ["empresa_id"],
        ondelete="CASCADE"
    )
    op.create_foreign_key(
        "fk_regras_hosts_grupo",
        "regras_acesso_hosts", "grupos",
        ["grupo_id"], ["grupo_id"],
        ondelete="CASCADE"
    )

    # acesso → usuarios
    op.create_foreign_key(
        "fk_acesso_usuario",
        "acesso", "usuarios",
        ["id_usuario"], ["usuario_id"],
        ondelete="CASCADE"
    )

    # --------------------------
    # INDEXES
    # --------------------------
    op.create_index("idx_usuarios_email", "usuarios", ["email"], unique=True)
    op.create_index("idx_empresas_cnpj", "empresas", ["cnpj"], unique=True)
    op.create_index("idx_feriados_emp_data", "feriados", ["empresa_id", "data"])
    op.create_index("idx_grupos_emp", "grupos", ["empresa_id"])
    op.create_index("idx_grupos_plano", "grupos", ["plano_id"])
    op.create_index("idx_gusuarios_emp", "grupos_usuarios", ["empresa_id"])
    op.create_index("idx_gusuarios_user", "grupos_usuarios", ["usuario_id"])
    op.create_index("idx_regras_emp", "regras_acesso", ["empresa_id"])
    op.create_index("idx_regras_hosts_emp", "regras_acesso_hosts", ["empresa_id"])

    # --------------------------
    # FUNCTIONS: validar_acesso
    # --------------------------
    op.execute("""
    CREATE OR REPLACE FUNCTION validar_acesso(p_usuario_id bigint, p_certificado_id bigint)
    RETURNS boolean
    LANGUAGE plpgsql
    AS $$
    DECLARE
        v_count integer;
    BEGIN
        SELECT COUNT(*) INTO v_count
        FROM grupos_usuarios gu
        JOIN grupos_certificados gc ON gc.grupo_id = gu.grupo_id
        WHERE gu.usuario_id = p_usuario_id
          AND gc.certificado_id = p_certificado_id;

        RETURN v_count > 0;
    END;
    $$;
    """)

    # --------------------------
    # FUNCTIONS: certificados_disponiveis
    # --------------------------
    op.execute("""
    CREATE OR REPLACE FUNCTION certificados_disponiveis(p_usuario_id bigint)
    RETURNS TABLE(certificado_id bigint, nome_arquivo text)
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT c.certificado_id, c.nome_arquivo
        FROM certificados c
        JOIN grupos_certificados gc ON gc.certificado_id = c.certificado_id
        JOIN grupos_usuarios gu ON gu.grupo_id = gc.grupo_id
        WHERE gu.usuario_id = p_usuario_id;
    END;
    $$;
    """)


def downgrade():

    # Remove functions
    op.execute("DROP FUNCTION IF EXISTS certificados_disponiveis(bigint)")
    op.execute("DROP FUNCTION IF EXISTS validar_acesso(bigint, bigint)")

    # Drop tables in reverse order (respecting FKs)
    op.drop_table("acesso")
    op.drop_table("regras_acesso_hosts")
    op.drop_table("regras_acesso")
    op.drop_table("grupos_certificados")
    op.drop_table("grupos_usuarios")
    op.drop_table("grupos")
    op.drop_table("planos_trabalho")
    op.drop_table("feriados")
    op.drop_table("certificados")
    op.drop_table("empresa_convites")
    op.drop_table("empresa_membros")
    op.drop_table("empresas")
    op.drop_table("usuarios")

    # Drop sequences
    op.execute("DROP SEQUENCE IF EXISTS acesso_acesso_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS regras_acesso_hosts_regra_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS regras_acesso_regra_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS grupos_certificados_grupo_cert_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS grupos_usuarios_grupo_usuario_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS grupos_grupo_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS planos_trabalho_plano_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS feriados_feriado_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS certificados_certificado_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS empresa_convites_convite_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS empresa_membros_membro_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS empresas_empresa_id_seq")
    op.execute("DROP SEQUENCE IF EXISTS usuarios_usuario_id_seq")

    # Drop enum type
    op.execute("DROP TYPE IF EXISTS usuario_nivel")
