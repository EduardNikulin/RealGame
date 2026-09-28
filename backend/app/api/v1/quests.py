# CRUD эндпоинты для управления квестами и шагами.
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.deps import get_current_user
from app.database.session import get_db
from app.models.quest import Quest
from app.models.purchase import UserPurchase
from app.models.user import User
from app.schemas.quest import QuestCardResponse

router = APIRouter(prefix="/quests", tags=["Quests"])

@router.get("/", response_model=List[QuestCardResponse])
async def get_quests_catalog(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение каталога опубликованных квестов с проверкой статуса покупки.
    """
    # 1. Выбираем из базы только опубликованные квесты
    quests_query = select(Quest).where(Quest.is_published == True)
    quests_result = await db.execute(quests_query)
    quests = quests_result.scalars().all()
    
    # 2. Находим все покупки текущего пользователя, чтобы понять, за что он платил
    purchases_query = select(UserPurchase.quest_id).where(UserPurchase.user_id == current_user.id)
    purchases_result = await db.execute(purchases_query)
    purchased_quest_ids = set(purchases_result.scalars().all())
    
    # 3. Формируем красивый ответ для фронтенда, проставляя флаг is_purchased
    catalog = []
    for quest in quests:
        # Квест считается купленным, если он бесплатный ИЛИ если ID квеста есть в списке покупок юзера
        is_purchased = quest.price == 0 or quest.id in ...
        
        catalog.append({
            "id": quest.id,
            "author_id": quest.author_id,
            "title": quest.title,
            "description": quest.description,
            "price": quest.price,
            "is_published": quest.is_published,
            "is_purchased": is_purchased
        })
        
    return catalog
