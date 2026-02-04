import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Adiciona raiz do projeto ao PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

# Carrega o .env explicitamente do diretório raiz do projeto
dotenv_path = os.path.join(PROJECT_ROOT, ".env")
load_dotenv(dotenv_path)

from backend.app.db.database import Base
from backend.app.core.config import DATABASE_URL

# Alembic Config
config = context.config

# Define URL do banco dinamicamente
config.set_main_option("sqlalchemy.url", DATABASE_URL)

print("ALEMBIC DATABASE_URL =", DATABASE_URL)

# Metadata usada pelo autogenerate
target_metadata = Base.metadata


def run_migrations_offline():
    """
    Executa migrations em modo offline.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """
    Executa migrations em modo online (conectado ao banco).
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# Decide qual modo usar
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
