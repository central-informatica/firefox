"""add function pode_gerenciar_usuarios

Revision ID: 9a51d7cb501f
Revises: 4559dad79bda
Create Date: 2025-12-29 18:00:55.933470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a51d7cb501f'
down_revision: Union[str, Sequence[str], None] = '4559dad79bda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.pode_gerenciar_usuarios(
            p_usuario_id BIGINT,
            p_empresa_id BIGINT
        ) RETURNS BOOLEAN
        LANGUAGE plpgsql
        AS $$
        DECLARE
            v_papel VARCHAR(30);
        BEGIN
            SELECT em.papel
              INTO v_papel
              FROM empresa_membros em
             WHERE em.usuario_id = p_usuario_id
               AND em.empresa_id = p_empresa_id
             LIMIT 1;

            IF v_papel IS NULL THEN
                RETURN FALSE;
            END IF;

            RETURN (v_papel IN ('ADMINISTRADOR', 'COMUN'));
        END;
        $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP FUNCTION IF EXISTS public.pode_gerenciar_usuarios(BIGINT, BIGINT);
        """
    )
