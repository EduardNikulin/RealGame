import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, Field

from app.api.v1.deps import get_current_user
from app.database.session import get_db
from app.models.review import Review
from app.models.quest import Quest
from app.models.user import User

router = APIRouter(prefix="/reviews", tags=["Reviews & Ratings"])

class ReviewCreate(BaseModel):
    quest_id: uuid.UUID
    rating: int = Field(..., ge=1, le=5)                                                # Валидация: оценка строго от 1 до 5
    comment: str = Field(None, max_length=1000)                                         # Лимит комментария 1000 знаков

@router.post("/")
async def leave_review(payload: ReviewCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Оставить отзыв к пройденному или купленному квесту """
    quest = await db.get(Quest, payload.quest_id)                                       # Ищем квест в базе
    if not quest: raise HTTPException(status_code=404, detail="Квест не найден")
    
    # Защита: один пользователь может оставить только один отзыв на конкретный квест
    check_q = select(Review).where(Review.user_id == current_user.id, Review.quest_id == payload.quest_id)
    res = await db.execute(check_q)
    if res.scalar_one_or_none(): raise HTTPException(status_code=400, detail="Вы уже оставили отзыв")
        
    new_review = Review(user_id=current_user.id, quest_id=payload.quest_id, rating=payload.rating, comment=payload.comment)
    db.add(new_review)
    await db.commit()
    return {"status": "success", "message": "Отзыв успешно добавлен"}

@router.get("/{quest_id}")
async def get_quest_reviews(quest_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """ Получить список всех отзывов к конкретному квесту """
    query = select(Review).where(Review.quest_id == quest_id).order_by(Review.created_at.desc())
    res = await db.execute(query)
    return res.scalars().all()
