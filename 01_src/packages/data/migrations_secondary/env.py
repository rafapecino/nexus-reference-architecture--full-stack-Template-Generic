"""Environment configuration for Alembic migrations."""

from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from common.config.settings import get_settings
from data.models import BaseXchg  # instalado en editable

# Cargamos .env para que las migraciones locales lean POSTGRES_* sin depender de imports que toquen load_dotenv().
load_dotenv()
settings = get_settings()

# Alembic Config object
config = context.config

# Setup loggers
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Sobrescribimos la URL del ini con la del paquete data
config.set_main_option("sqlalchemy.url", settings.db_staging.url)

# Set target metadata for Alembic migrations
target_metadata = BaseXchg.metadata


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
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.begin() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
