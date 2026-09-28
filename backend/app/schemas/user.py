# Pydantic схемы валидации данных пользователей для API.
import uuid
from pydantic import BaseModel, Field, ConfigDict

# Базовая схема с общими полями, которая будет использоваться в других схемах
class UserBase(BaseModel):
    # Проверяем, что имя пользователя — это строка от 3 до 50 символов
    username: str = Field(..., min_length=3, max_length=50, description="Уникальное имя пользователя")

# Схема, которая приходит от фронтенда при регистрации нового пользователя
class UserCreate(UserBase):
    # Пароль должен быть не короче 6 символов для безопасности
    password: str = Field(..., min_length=6, max_length=100, description="Пароль в открытом виде")

# Схема, которая приходит при авторизации (входе) через обычный JSON
class UserLogin(BaseModel):
    username: str = Field(..., description="Имя пользователя")
    password: str = Field(..., description="Пароль")

# Схема ответа бэкенда: то, что наш API отдаст фронтенду (пароль возвращать нельзя!)
class UserResponse(UserBase):
    id: uuid.UUID = Field(..., description="Уникальный ID пользователя в формате UUID")
    role: str = Field(..., description="Роль пользователя в системе (player/author)")

    # Включаем специальную настройку Pydantic v2. Она позволяет библиотеке автоматически
    # читать данные из SQLAlchemy моделей (объектов класса User) и превращать их в JSON.
    model_config = ConfigDict(from_attributes=True)

# Схема, которую бэкенд вернет после успешного ввода логина и пароля
class Token(BaseModel):
    access_token: str = Field(..., description="Сам JWT-токен доступа")
    token_type: str = Field("bearer", description="Тип токена (всегда bearer)")
