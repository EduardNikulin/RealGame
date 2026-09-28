from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Шаблон для авто-генерации имен ограничений в базе данных
POSTGRES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",                                                      # Шаблон для обычных индексов
    "uq": "uq_%(table_name)s_%(column_0_name)s",                                        # Шаблон для уникальных полей
    "ck": "ck_%(table_name)s_%(constraint_name)s",                                      # Шаблон для проверок (check)
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",                # Шаблон для внешних ключей (Foreign Key)
    "pk": "pk_%(table_name)s"                                                           # Шаблон для первичных ключей (Primary Key)
}

class Base(DeclarativeBase):
    """Базовый класс для всех моделей с жестко настроенными именами ограничений."""
    # Привязываем наше соглашение к метаданным, чтобы Alembic видел имена ограничений
    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)
