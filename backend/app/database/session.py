from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. Создаем асинхронный движок (Engine)
# Он берет нашу строку DATABASE_URL из настроек (которая начинается с postgresql+asyncpg://)
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Включаем echo=True, чтобы в терминале VS Code красиво писались все SQL-запросы (очень помогает при отладке)
    future=True
)

# 2. Создаем фабрику сессий (Session Maker)
# Мы отключаем автокоммит и автофлеш, и говорим, что сессии должны быть строго AsyncSession
async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 3. Асинхронный генератор для получения сессии базы данных (Dependency)
# Эту функцию мы будем внедрять (Inject) в наши роуты FastAPI, чтобы давать им доступ к БД
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()  # Если всё прошло успешно, сохраняем изменения автоматически
        except Exception:
            await session.rollback()  # Если в процессе роута произошла ошибка, откатываем всё назад
            raise
        finally:
            await session.close()  # В любом случае закрываем соединение, чтобы не забивать пул
