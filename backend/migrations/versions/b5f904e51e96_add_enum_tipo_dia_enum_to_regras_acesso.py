"""Add enum tipo_dia_enum to regras_acesso

Revision ID: b5f904e51e96
Revises: 2a3106605800
Create Date: 2025-12-11 16:54:43.812054

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision = "b5f904e51e96"
down_revision = "957e00c66e96"
branch_labels = None
depends_on = None


def upgrade():
    # Criar ENUM no PostgreSQL
    op.execute("CREATE TYPE tipo_dia_enum AS ENUM ('corridos', 'uteis', 'especificos');")
    
    # Alterar coluna
    op.alter_column(
        'regras_acesso',
        'tipo_dia',
        type_=sa.Enum('corridos', 'uteis', 'especificos', name='tipo_dia_enum', native_enum=True),
        existing_type=sa.String(),
        postgresql_using="tipo_dia::tipo_dia_enum"
    )


def downgrade():
    # Voltar para string
    op.alter_column(
        'regras_acesso',
        'tipo_dia',
        type_=sa.String(),
        existing_type=sa.Enum(name='tipo_dia_enum'),
        postgresql_using="tipo_dia::text"
    )

    # Remover ENUM
    op.execute("DROP TYPE tipo_dia_enum;")
