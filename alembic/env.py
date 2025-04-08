from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Интерпретируем конфигурацию файла для Python логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Импортируем Base и все модели, чтобы Alembic "видел" таблицы
from database import Base
from models import User, Category, Roadmap, Step, Comment, Like  # 👈 ОБЯЗАТЕЛЬНО!

# Указываем метаданные из моделей
target_metadata = Base.metadata

# Получаем строку подключения из переменных окружения
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Обновляем строку подключения в конфигурации Alembic
config.set_main_option("sqlalchemy.url", database_url)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
