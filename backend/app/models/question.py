import uuid
from sqlalchemy import String, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class Question(Base):
    __tablename__ = "questions"

    # Уникальный ID вопроса
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    
    # К какому конкретно шагу привязан этот вопрос
    step_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("steps.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Порядковый номер вопроса внутри этого шага
    question_order: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
    )
    
    # Текст самого вопроса (например: "Какого цвета была мантия у короля?")
    question_text: Mapped[str] = mapped_column(
        Text, 
        nullable=False
    )
    
    # Тип вопроса: может быть 'text' (свободный ввод) или 'quiz' (выбор варианта)
    question_type: Mapped[str] = mapped_column(
        String(20), 
        default="text", 
        nullable=False
    )
    
    # Правильный ответ, с которым бэкенд будет сравнивать то, что ввел игрок
    correct_answer: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    # Количество игровых очков, получаемых за правильный ответ
    points: Mapped[int] = mapped_column(
        Integer, 
        default=10, 
        nullable=False
    )


class QuizOption(Base):
    __tablename__ = "quiz_options"

    # Уникальный ID варианта ответа
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    
    # К какому вопросу относится этот вариант ответа
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Текст варианта ответа (например: "Красная", "Синяя", "Зеленая")
    option_text: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
