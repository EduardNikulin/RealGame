import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Media(Base):
    __tablename__ = "media"

    # Уникальный ID медиафайла
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    
    # Привязка к квесту (опционально - nullable=True)
    quest_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quests.id", ondelete="CASCADE"), 
        nullable=True
    )
    
    # Привязка к шагу (опционально)
    step_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("steps.id", ondelete="CASCADE"), 
        nullable=True
    )
    
    # Привязка к конкретному вопросу (опционально)
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), 
        nullable=True
    )
    
    # Ссылка на сам файл в хранилище (например: "/uploads/image.png")
    file_url: Mapped[str] = mapped_column(
        String(500), 
        nullable=False
    )
    
    # Тип файла: 'image' (картинка), 'video' (видео) или 'audio' (звук)
    file_type: Mapped[str] = mapped_column(
        String(20), 
        nullable=False
    )
