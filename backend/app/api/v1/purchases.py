import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.v1.deps import get_current_user
from app.database.session import get_db
from app.models.quest import Quest
from app.models.purchase import UserPurchase
from app.models.user import User

router = APIRouter(prefix="/purchases", tags=["Purchases"])

@router.post("/{quest_id}")
async def purchase_quest(
    quest_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Симуляция покупки платного квеста (создание записи в UserPurchases).
    """
    # 1. Проверяем, существует ли вообще такой квест в базе
    quest_query = select(Quest).where(Quest.id == quest_id)
    quest_result = await db.execute(quest_query)
    quest = quest_result.scalar_one_or_none()
    
    if not quest:
        raise HTTPException(status_code=404, detail="Квест не найден")
        
    # 2. Проверяем, не пытается ли юзер бесплатно «купить» то, что и так бесплатно
    if quest.price == 0:
        raise HTTPException(status_code=400, detail="Этот квест бесплатный, его не нужно покупать")
        
    # 3. Проверяем, не куплен ли этот квест пользователем ранее
    check_query = select(UserPurchase).where(
        UserPurchase.user_id == current_user.id,
        UserPurchase.quest_id == quest_id
    )
    check_result = await db.execute(check_query)
    if check_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Вы уже купили этот квест ранее")
        
    # 4. Создаем запись о покупке (для MVP фиксируем текущую цену квеста)
    new_purchase = UserPurchase(
        user_id=current_user.id,
        quest_id=quest_id,
        paid_price=quest.price
    )
    
    db.add(new_purchase)
    return {"status": "success", "message": "Квест успешно приобретен"}
