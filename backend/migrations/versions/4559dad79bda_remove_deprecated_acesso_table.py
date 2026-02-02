"""remove deprecated acesso table

Revision ID: 4559dad79bda
Revises: a4c3bfff7b89
Create Date: 2025-12-14 14:25:24.452512

This migration removes the deprecated 'acesso' table which has been replaced
by the new 'access_tokens' table with opaque token support.

The acesso table used plain-text tokens and has been superseded by the
secure Argon2-hashed opaque token system.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4559dad79bda'
down_revision: Union[str, Sequence[str], None] = "a4c3bfff7b89" #'a4c3bfff7b89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Remove the deprecated acesso table.

    The table was already marked as inactive by the previous migration,
    so this simply removes the schema.
    """
    # Drop the acesso table
    op.drop_table('acesso')


def downgrade() -> None:
    """
    Recreate the acesso table for rollback purposes.

    Note: This will recreate the table structure but will NOT restore
    the old session data.
    """
    # Recreate acesso table
    op.create_table(
        'acesso',
        sa.Column('acesso_id', sa.BigInteger(), nullable=False),
        sa.Column('id_usuario', sa.BigInteger(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('ativo', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('criado_em', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.usuario_id'], name='acesso_id_usuario_fkey'),
        sa.PrimaryKeyConstraint('acesso_id', name='acesso_pkey'),
        sa.UniqueConstraint('token', name='acesso_token_key')
    )
