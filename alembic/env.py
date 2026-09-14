"""Alembic runtime.

Reads DATABASE_URL from the environment (or .env) so the same migration
files work on a laptop and inside Docker.
"""

from logging.config import fileConfig
from pathlib import Path
import sys

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

# Project root on sys.path so `import app` works from `alembic upgrade`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
load_dotenv()

from app.database import Base, get_database_url  # noqa: E402
from app import models  # noqa: E402, F401  — registers tables on Base.metadata

config = context.config

# ConfigParser treats % as interpolation, so passwords with % must be escaped.
database_url = get_database_url().replace("%", "%%")
config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
