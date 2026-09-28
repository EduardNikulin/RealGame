# SQLAlchemy модель отслеживания прогресса (UserProgress).
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    # Уникальный ID игровой сессии
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    
    # Какой пользователь играет
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Какой квест он проходит
    quest_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quests.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # ID шага, на котором сейчас находится игрок
    # nullable=True, потому что когда квест полностью пройден, текущего шага больше нет
    current_step_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("steps.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    # Суммарное количество очков, набранное за правильные ответы в этом квесте
    total_score: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        nullable=False
    )
    
    # Статус прохождения: 'in_progress' (играет прямо сейчас) или 'completed' (завершил)
    status: Mapped[str] = mapped_column(
        String(20), 
        default="in_progress", 
        nullable=False
    )
    
    # Время автоматического старта квеста
    started_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    
    # Время завершения квеста (заполняется только при переходе статуса в 'completed')
    finished_at: Mapped[datetime] = mapped_column(
        DateTime, 
        nullable=True
    )
