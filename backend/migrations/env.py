from __future__ import annotations

from alembic import context
from sqlalchemy import pool
from logging.config import fileConfig

from backend.app.db.session import engine
from backend.app.db.base import Base

# Configurações do Alembic (não alterar)
config = context.config

# Permite logging do alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadados usados pelo autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Executa migrations offline (gera SQL sem conectar no DB)."""
    url = engine.url.render_as_string(hide_password=False)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrations online (conectado ao DB)."""

    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            process_revision_directives=None,
            render_as_batch=False,
        )

        with context.begin_transaction():
            context.run_migrations()


# Seleciona offline ou online automaticamente
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
