import uuid
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False) # Кто оставил
    quest_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quests.id", ondelete="CASCADE"), nullable=False) # К какому квесту
    rating: Mapped[int] = mapped_column(Integer, nullable=False)                         # Оценка от 1 до 5
    comment: Mapped[str] = mapped_column(Text, nullable=True)                            # Текстовый отзыв пользователя
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
