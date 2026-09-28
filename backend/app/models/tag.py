import uuid
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Tag(Base):
    __tablename__ = "tags"

    # Для тегов можно использовать обычный Integer, чтобы не плодить UUID без нужды
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True, 
        autoincrement=True
    )
    
    # Название тега (например, "Детектив")
    name: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        index=True, 
        nullable=False
    )


class QuestTag(Base):
    __tablename__ = "quest_tags"

    # Связующая таблица без собственного ID (составной первичный ключ)
    quest_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quests.id", ondelete="CASCADE"), 
        primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), 
        primary_key=True
    )
