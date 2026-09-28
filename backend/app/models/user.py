import uuid
from sqlalchemy import String, Integer                                                  # Добавили импорт Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="player", nullable=False)
    total_lifetime_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False) # Общий счет за ВСЕ квесты
