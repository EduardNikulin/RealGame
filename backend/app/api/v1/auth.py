# Эндпоинты авторизации: регистрация, хеширование паролей bcrypt, выдача JWT токенов.
import uuid
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import hash_password, verify_password, create_access_token
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token

# Создаем изолированный роутер для авторизации
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Регистрация нового пользователя.
    """
    # 1. Проверяем, нет ли уже пользователя с таким именем в базе данных
    query = select(User).where(User.username == user_in.username)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )
    
    # 2. Хэшируем чистый пароль из Pydantic-схемы
    hashed_pwd = hash_password(user_in.password)
    
    # 3. Создаем новый объект модели SQLAlchemy User
    new_user = User(
        username=user_in.username,
        password_hash=hashed_pwd,
        role="player"  # По умолчанию все регистрируются как обычные игроки
    )
    
    # 4. Сохраняем пользователя в PostgreSQL
    db.add(new_user)
    await db.flush()  # Метод flush() заставляет БД сгенерировать UUID для нового юзера
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    """
    Вход в систему (авторизация). При успехе возвращает JWT-токен.
    Использует OAuth2 стандарт (данные передаются как form-data).
    """
    # 1. Ищем пользователя в базе данных по введенному username
    query = select(User).where(User.username == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    # 2. Если пользователя нет или пароль не совпал с хэшем — кидаем ошибку 401
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Задаем время жизни токена (например, 60 минут)
    access_token_expires = timedelta(minutes=60)
    
    # 4. Генерируем строку JWT-токена, зашивая внутрь UUID пользователя (sub)
    access_token = create_access_token(
        subject=str(user.id), 
        expires_delta=access_token_expires
    )
    
    # 5. Возвращаем токен согласно нашей Pydantic схеме Token
    return {"access_token": access_token, "token_type": "bearer"}
