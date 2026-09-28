# SQLAlchemy модель пользователя (User).
import uuid
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class User(Base):
    __tablename__ = "users"  # Имя таблицы в PostgreSQL

    # Идентификатор пользователя (UUID)
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    
    # Уникальное имя пользователя
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        index=True, 
        nullable=False
    )
    
    # Хэш пароля (в открытом виде пароли никогда не храним!)
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    # Роль пользователя: 'player' (игрок) или 'author' (создатель квестов)
    role: Mapped[str] = mapped_column(
        String(20), 
        default="player", 
        nullable=False
    )
