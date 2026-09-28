# SQLAlchemy модель шага квеста (Step).
import uuid
from sqlalchemy import String, ForeignKey, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Step(Base):
    __tablename__ = "steps"  # Имя таблицы в базе данных PostgreSQL

    # Уникальный идентификатор шага
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    
    # К какому квесту относится этот шаг (Внешний ключ)
    # ondelete="CASCADE" означает: если удалить квест, автоматически удалятся и все его шаги
    quest_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quests.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Порядковый номер шага в игре (например: 1-й шаг, 2-й шаг)
    step_order: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
    )
    
    # Название шага (например: "У старого дуба")
    step_title: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    # Географическая широта цели (координата X на карте)
    target_lat: Mapped[float] = mapped_column(
        Float, 
        nullable=False
    )
    
    # Географическая долгота цели (координата Y на карте)
    target_lon: Mapped[float] = mapped_column(
        Float, 
        nullable=False
    )
    
    # Радиус приближения в метрах (насколько близко игрок должен подойти к точке, чтобы шаг засчитался)
    proximity_radius: Mapped[int] = mapped_column(
        Integer, 
        default=30, 
        nullable=False
    )
