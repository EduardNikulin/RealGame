import uuid
from pydantic import BaseModel, Field, ConfigDict
from typing import List

# Вариант ответа для вопросов-тестов
class QuizOptionResponse(BaseModel):
    id: uuid.UUID = Field(..., description="ID варианта ответа")
    option_text: str = Field(..., description="Текст варианта ответа")

    model_config = ConfigDict(from_attributes=True)

# Структура вопроса для игрока
class QuestionResponse(BaseModel):
    id: uuid.UUID = Field(..., description="ID вопроса")
    question_order: int = Field(..., description="Порядковый номер вопроса")
    question_text: str = Field(..., description="Текст вопроса")
    question_type: str = Field(..., description="Тип вопроса (text или quiz)")
    options: List[QuizOptionResponse] = Field(default=[], description="Варианты ответов")

    model_config = ConfigDict(from_attributes=True)

# Ответ бэкенда на запрос текущего активного шага
class CurrentStepResponse(BaseModel):
    step_title: str = Field(..., description="Название локации")
    question: QuestionResponse = Field(..., description="Текущий вопрос")
    media_urls: List[str] = Field(default=[], description="Ссылки на медиа")
    target_lat: float = Field(..., description="Широта цели")
    target_lon: float = Field(..., description="Долгота цели")

# То, что присылает фронтенд при проверке ответа
class VerifyRequest(BaseModel):
    user_answer: str = Field(..., description="Ответ игрока")
    latitude: float = Field(..., description="Широта игрока")
    longitude: float = Field(..., description="Долгота игрока")

# Схема ответа после проверки 
class VerifyResponse(BaseModel):
    success: bool = Field(..., description="Правильно ли ответил игрок (True/False)")
    message: str = Field(..., description="Сообщение с результатом проверки")
    status: str = Field(..., description="Статус игры (NEW_STEP/SAME_STEP/QUEST_COMPLETED)")
    total_score: int = Field(..., description="Текущие очки игрока")
