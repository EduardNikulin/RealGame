# Pydantic схемы валидации данных квестов для API.
import uuid
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

# Базовые поля квеста, общие для всех схем
class QuestBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, description="Название квеста")
    description: str = Field(..., min_length=10, description="Подробное описание квеста")
    # Цена квеста. По умолчанию 0.00 (бесплатный). Должна быть больше или равна 0.
    price: Decimal = Field(Decimal("0.00"), ge=0, description="Цена квеста (0.00 если бесплатный)")

# То, что присылает автор при создании квеста (пока просто черновик)
class QuestCreate(QuestBase):
    pass

# Схема для отображения квеста в каталоге. Сюда мы подмешиваем логику покупок.
class QuestCardResponse(QuestBase):
    id: uuid.UUID = Field(..., description="ID квеста")
    author_id: uuid.UUID = Field(..., description="ID автора, создавшего квест")
    is_published: bool = Field(..., description="Статус публикации (опубликован/черновик)")
    
    # КРИТИЧЕСКОЕ ПОЛЕ ДЛЯ МОНЕТИЗАЦИИ:
    # Фронтенд на React будет смотреть на этот флаг. Если True -> кнопка 'Начать', если False -> 'Купить'.
    is_purchased: bool = Field(default=False, description="Куплен ли этот квест текущим игроком")

    # Включаем автоматическое чтение данных из моделей SQLAlchemy ORM
    model_config = ConfigDict(from_attributes=True)
