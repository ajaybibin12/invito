from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# -------------------------------
# IMPORT YOUR APP CONFIG & MODELS
# -------------------------------
from app.core.config import settings
print("ALEMBIC DB URL =", settings.DATABASE_URL)

from app.core.database import Base

# import ALL models so Alembic sees them
from app.models.user import User  # noqa: F401
from app.models.event import Event  # noqa: F401
from app.models.invite import Invite  # noqa: F401
from app.models.refresh_token import RefreshToken  # noqa: F401

# -------------------------------
# ALEMBIC CONFIG
# -------------------------------
config = context.config

# Setup Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject DATABASE_URL from .env
config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL
)

# Tell Alembic what metadata to track
target_metadata = Base.metadata


# -------------------------------
# OFFLINE MIGRATIONS
# -------------------------------
def run_migrations_offline() -> None:
    """Run migrations in offline mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# -------------------------------
# ONLINE MIGRATIONS
# -------------------------------
def run_migrations_online() -> None:
    """Run migrations in online mode."""
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
        )

        with context.begin_transaction():
            context.run_migrations()


# -------------------------------
# ENTRYPOINT
# -------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
