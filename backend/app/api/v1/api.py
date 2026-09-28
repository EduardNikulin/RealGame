from fastapi import APIRouter
from app.api.v1 import auth, quests, purchases, game

api_router = APIRouter()

api_router.include_router(auth.router)        # авторизация
api_router.include_router(quests.router)      # каталог квестов
api_router.include_router(purchases.router)   # покупки
api_router.include_router(game.router)        # движок игрылы