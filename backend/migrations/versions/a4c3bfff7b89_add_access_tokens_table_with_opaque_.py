"""add access_tokens table with opaque token support

Revision ID: a4c3bfff7b89
Revises: 15e059b580f1
Create Date: 2025-12-14 12:03:20.475518

This migration implements a secure opaque token authentication system:
- Replaces plain-text tokens with Argon2-hashed tokens
- Uses selector:validator pattern for optimal performance
- Supports dual authentication flows (WEB cookies + DESKTOP Bearer tokens)
- Embeds permissions in JSONB for single-query authorization
- Invalidates all existing sessions (clean migration)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision: str = 'a4c3bfff7b89'
down_revision: Union[str, Sequence[str], None] = "8dab8acbe204" #'15e059b580f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade schema to add access_tokens table and invalidate old sessions.

    Steps:
    1. Create client_type enum
    2. Create access_tokens table with all columns
    3. Create indexes for performance
    4. Create GIN indexes for JSONB queries
    5. Invalidate all existing sessions in acesso table
    """
    # 1. Create ENUM type for client_type (if it doesn't already exist)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'client_type') THEN
                CREATE TYPE client_type AS ENUM ('WEB', 'DESKTOP');
            END IF;
        END$$;
    """)

    # 2. Create access_tokens table
    op.create_table(
        'access_tokens',
        sa.Column('token_id', sa.BigInteger(), nullable=False),
        sa.Column('usuario_id', sa.BigInteger(), nullable=False, comment='User owning this token'),
        sa.Column('selector', sa.String(length=64), nullable=False, comment='First 32 bytes (base64url) for fast indexed lookup'),
        sa.Column('validator_hash', sa.String(length=128), nullable=False, comment='Argon2 hash of validator (last 32 bytes)'),
        sa.Column('tipo_cliente', ENUM('WEB', 'DESKTOP', name='client_type', create_type=False), nullable=False, comment='Client type: WEB (cookies+CSRF) or DESKTOP (Bearer token)'),
        sa.Column('criado_em', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='Token creation timestamp'),
        sa.Column('expires_at', sa.DateTime(), nullable=False, comment='Token expiration timestamp (typically 15 minutes)'),
        sa.Column('ultimo_uso', sa.DateTime(), nullable=True, comment='Last time this token was used for authentication'),
        sa.Column('revogado', sa.Boolean(), server_default=sa.text('false'), nullable=False, comment='Token revocation flag'),
        sa.Column('revogado_em', sa.DateTime(), nullable=True, comment='Timestamp when token was revoked'),
        sa.Column('revogado_motivo', sa.String(length=255), nullable=True, comment='Reason for revocation (logout, security, expired, etc)'),
        sa.Column('permissions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='Embedded permissions: user role + empresa memberships'),
        sa.Column('user_agent', sa.Text(), nullable=True, comment='Client user agent string'),
        sa.Column('ip_address', sa.String(length=45), nullable=True, comment='Client IP address (IPv4 or IPv6)'),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.usuario_id'],
                               ondelete='CASCADE', name='access_tokens_usuario_fk'),
        sa.PrimaryKeyConstraint('token_id', name='access_tokens_pkey'),
        sa.UniqueConstraint('selector', name='access_tokens_selector_key'),
        comment='Opaque access tokens with Argon2 hashing for secure authentication'
    )

    # 3. Create standard indexes
    op.create_index('idx_access_tokens_usuario', 'access_tokens', ['usuario_id'])
    op.create_index('idx_access_tokens_selector', 'access_tokens', ['selector'], unique=True)
    op.create_index('idx_access_tokens_expires_at', 'access_tokens', ['expires_at'])

    # 4. Create GIN indexes for JSONB queries
    op.execute("""
        CREATE INDEX idx_access_tokens_permissions_empresas
        ON access_tokens USING GIN ((permissions -> 'empresas'))
    """)
    op.execute("""
        CREATE INDEX idx_access_tokens_permissions_nivel
        ON access_tokens ((permissions ->> 'usuario_nivel'))
    """)

    # 5. Invalidate all existing sessions (clean migration)
    # This forces all users to re-login with the new token system
    # op.execute("UPDATE acesso SET ativo = false WHERE ativo = true")


def downgrade() -> None:
    """
    Downgrade schema to remove access_tokens table.

    Note: This does NOT re-activate old sessions in acesso table.
    Old sessions remain inactive.
    """
    # Drop GIN indexes
    op.execute("DROP INDEX IF EXISTS idx_access_tokens_permissions_nivel")
    op.execute("DROP INDEX IF EXISTS idx_access_tokens_permissions_empresas")

    # Drop standard indexes
    op.drop_index('idx_access_tokens_expires_at', table_name='access_tokens')
    op.drop_index('idx_access_tokens_selector', table_name='access_tokens')
    op.drop_index('idx_access_tokens_usuario', table_name='access_tokens')

    # Drop access_tokens table
    op.drop_table('access_tokens')

    # Drop ENUM type
    op.execute("DROP TYPE client_type")
