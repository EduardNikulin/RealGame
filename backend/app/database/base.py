from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy в проекте."""
    pass

# Явно импортируем все модели, чтобы Alembic увидел их через Base.metadata
from app.models.user import User
from app.models.quest import Quest
from app.models.purchase import UserPurchase
from app.models.tag import Tag, QuestTag
from app.models.step import Step
from app.models.question import Question, QuizOption
from app.models.media import Media
from app.models.progress import UserProgress