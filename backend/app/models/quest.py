# SQLAlchemy модель квеста (Quest).
import uuid
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Quest(Base):
    __tablename__ = "quests"  # Имя таблицы в PostgreSQL

    # Уникальный ID квеста
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    
    # ID автора, который создал этот квест (ссылка на таблицу users)
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Название квеста
    title: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    # Подробное описание квеста
    description: Mapped[str] = mapped_column(
        Text, 
        nullable=False
    )
    
    # Цена квеста (0.00 — если он бесплатный)
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), 
        default=0.00, 
        nullable=False
    )
    
    # Флаг публикации: False — черновик, True — виден в каталоге
    is_published: Mapped[bool] = mapped_column(
        default=False, 
        nullable=False
    )
