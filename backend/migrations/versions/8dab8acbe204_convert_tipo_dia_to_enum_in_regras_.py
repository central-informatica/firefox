"""Convert tipo_dia to enum in regras_acesso_hosts

Revision ID: 8dab8acbe204
Revises: b5f904e51e96
Create Date: 2025-12-11 17:06:03.890324

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8dab8acbe204'
down_revision: Union[str, Sequence[str], None] = 'b5f904e51e96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Garantir que o ENUM já exista
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_dia_enum') THEN
                CREATE TYPE tipo_dia_enum AS ENUM ('corridos', 'uteis', 'especificos');
            END IF;
        END$$;
    """)

    # Converter a coluna para ENUM
    op.alter_column(
        "regras_acesso_hosts",
        "tipo_dia",
        type_=sa.Enum("corridos", "uteis", "especificos",
                      name="tipo_dia_enum", native_enum=True),
        existing_type=sa.String(),
        postgresql_using="tipo_dia::tipo_dia_enum"
    )


def downgrade():
    # Reverter ENUM para string
    op.alter_column(
        "regras_acesso_hosts",
        "tipo_dia",
        type_=sa.String(),
        existing_type=sa.Enum(name="tipo_dia_enum"),
        postgresql_using="tipo_dia::text"
    )
