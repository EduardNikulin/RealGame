import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status                  # Добавили импорт HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.deps import get_current_user
from app.database.session import get_db
from app.models.quest import Quest
from app.models.purchase import UserPurchase
from app.models.tag import QuestTag                                             # Импортируем модель связей тегов
from app.models.user import User
from app.schemas.quest import QuestCardResponse

router = APIRouter(prefix="/quests", tags=["Quests"])

@router.get("/", response_model=List[QuestCardResponse])
async def get_quests_catalog(
    tag_id: Optional[int] = None,                                               # Параметр фильтрации по тегу
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Если тег передан, ищем ID квестов, привязанных к нему
    if tag_id:
        t_query = select(QuestTag.quest_id).where(QuestTag.tag_id == tag_id)
        t_res = await db.execute(t_query)
        target_quest_ids = t_res.scalars().all()
        
        # Загружаем только квесты из списка найденных ID
        quests_query = select(Quest).where(Quest.is_published == True, Quest.id.in_(target_quest_ids))
    else:
        # Иначе загружаем вообще все опубликованные квесты
        quests_query = select(Quest).where(Quest.is_published == True)
        
    quests_result = await db.execute(quests_query)
    quests = quests_result.scalars().all()
    
    purchases_query = select(UserPurchase.quest_id).where(UserPurchase.user_id == current_user.id)
    purchases_result = await db.execute(purchases_query)
    purchased_quest_ids = set(purchases_result.scalars().all())
    
    catalog = []
    for quest in quests:
        is_purchased = quest.price == 0 or quest.id in purchased_quest_ids
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


@router.get("/{quest_id}", response_model=QuestCardResponse)
async def get_quest_detail(
    quest_id: uuid.UUID,                                                        # Пишем строго uuid.UUID
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    quest = await db.get(Quest, quest_id)                                       # Ищем квест в базе данных
    if not quest or not quest.is_published:
        raise HTTPException(status_code=404, detail="Quest not found")          # Защита от дурака
        
    p_query = select(UserPurchase).where(UserPurchase.user_id == current_user.id, UserPurchase.quest_id == quest_id)
    p_res = await db.execute(p_query)
    is_purchased = quest.price == 0 or p_res.scalar_one_or_none() is not None
    
    return {
        "id": quest.id,
        "author_id": quest.author_id,
        "title": quest.title,
        "description": quest.description,
        "price": quest.price,
        "is_published": quest.is_published,
        "is_purchased": is_purchased
    }
