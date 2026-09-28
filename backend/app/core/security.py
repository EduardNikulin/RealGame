from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

# Настраиваем контекст для шифрования паролей с помощью алгоритма bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хэширует чистый пароль пользователя для сохранения в БД."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, совпадает ли введенный пароль с хэшем из БД."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Создает подписанный JWT-токен для авторизации пользователя."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Токен будет жить по умолчанию 30 минут, если не передано другое время
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    # Данные, которые мы зашиваем внутрь токена (обычно это ID или email пользователя)
    to_encode = {"exp": expire, "sub": str(subject)}
    
    # Подписываем токен нашим SECRET_KEY с использованием выбранного алгоритма
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
