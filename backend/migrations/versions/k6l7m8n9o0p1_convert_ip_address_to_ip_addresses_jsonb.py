"""convert_ip_address_to_ip_addresses_jsonb

Revision ID: k6l7m8n9o0p1
Revises: j5k6l7m8n9o0
Create Date: 2026-02-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'k6l7m8n9o0p1'
down_revision: Union[str, Sequence[str], None] = 'j5k6l7m8n9o0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert ip_address (String) to ip_addresses (JSONB array)."""
    # 1. Add new JSONB column
    op.add_column('regras_acesso_ips', sa.Column(
        'ip_addresses', JSONB(), nullable=True,
        comment='Lista de enderecos IP (IPv4, IPv6 ou blocos CIDR)'
    ))

    # 2. Migrate existing data: wrap single ip_address into a JSON array
    op.execute(
        "UPDATE regras_acesso_ips SET ip_addresses = jsonb_build_array(ip_address) WHERE ip_address IS NOT NULL"
    )

    # 3. Set NOT NULL after data migration
    op.alter_column('regras_acesso_ips', 'ip_addresses', nullable=False)

    # 4. Drop old unique constraint and index that reference ip_address
    op.drop_constraint('regras_acesso_ips_grupo_ip_unq', 'regras_acesso_ips', type_='unique')
    op.drop_index('idx_regras_acesso_ips_ip', table_name='regras_acesso_ips')

    # 5. Drop old column
    op.drop_column('regras_acesso_ips', 'ip_address')


def downgrade() -> None:
    """Revert ip_addresses (JSONB) back to ip_address (String)."""
    # 1. Add old column back
    op.add_column('regras_acesso_ips', sa.Column(
        'ip_address', sa.String(45), nullable=True,
        comment='Endereco IP (IPv4 ou IPv6)'
    ))

    # 2. Migrate data: extract first element from JSONB array
    op.execute(
        "UPDATE regras_acesso_ips SET ip_address = ip_addresses->>0 WHERE ip_addresses IS NOT NULL"
    )

    # 3. Set NOT NULL
    op.alter_column('regras_acesso_ips', 'ip_address', nullable=False)

    # 4. Recreate old index and constraint
    op.create_index('idx_regras_acesso_ips_ip', 'regras_acesso_ips', ['ip_address'])
    op.create_unique_constraint('regras_acesso_ips_grupo_ip_unq', 'regras_acesso_ips', ['grupo_id', 'ip_address'])

    # 5. Drop new column
    op.drop_column('regras_acesso_ips', 'ip_addresses')