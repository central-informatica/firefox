from alembic import op
import sqlalchemy as sa

revision = "957e00c66e96"
down_revision = "2a3106605800"
branch_labels = None
depends_on = None


def upgrade():
    # 1️⃣ Criar o ENUM se ainda não existir
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

    # 2️⃣ Remover DEFAULT antes da conversão
    op.execute("""
        ALTER TABLE usuarios
        ALTER COLUMN nivel DROP DEFAULT;
    """)

    # 3️⃣ Converter VARCHAR -> ENUM
    op.execute("""
        ALTER TABLE usuarios
        ALTER COLUMN nivel TYPE usuario_nivel
        USING nivel::usuario_nivel;
    """)

    # 4️⃣ Recolocar DEFAULT no novo tipo
    op.execute("""
        ALTER TABLE usuarios
        ALTER COLUMN nivel SET DEFAULT 'COMUM';
    """)

    # 5️⃣ Repetir o processo para empresa_membros

    op.execute("""
        ALTER TABLE empresa_membros
        ALTER COLUMN papel DROP DEFAULT;
    """)

    op.execute("""
        ALTER TABLE empresa_membros
        ALTER COLUMN papel TYPE usuario_nivel
        USING papel::usuario_nivel;
    """)

    op.execute("""
        ALTER TABLE empresa_membros
        ALTER COLUMN papel SET DEFAULT 'COMUM';
    """)
