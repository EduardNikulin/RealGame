from fastapi import APIRouter
from app.api.v1 import auth, quests, purchases, game, constructor, tags, user, reviews, leaderboard    # Импортируем абсолютно все роутеры

api_router = APIRouter()

api_router.include_router(auth.router)        # Авторизация и сессии
api_router.include_router(quests.router)      # Каталог квестов и деталей
api_router.include_router(purchases.router)   # Симуляция оплаты покупок
api_router.include_router(game.router)        # Игровой движок (таймеры + GPS)
api_router.include_router(constructor.router) # Конструктор для панели автора
api_router.include_router(tags.router)        # Список категорий и тегов
api_router.include_router(user.router)        # Профиль и история прохождений
api_router.include_router(reviews.router)     # Подключили отзывы
api_router.include_router(leaderboard.router) # Подключили доску лидеров