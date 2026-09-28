import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 1. Импортируем наши настройки и базовый класс моделей
from app.core.config import settings
from app.database.base import Base

# Это объект конфигурации Alembic, который предоставляет доступ к значениям в alembic.ini
config = context.config

# Перезаписываем sqlalchemy.url в alembic.ini нашей строкой из .env
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Настраиваем логирование, если файл конфигурации существует
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. Передаем метаданные наших моделей, чтобы Alembic видел таблицы
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Вспомогательная функция для выполнения миграций внутри async-подключения."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме (с использованием асинхронного движка)."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
