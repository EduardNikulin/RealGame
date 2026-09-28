from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.models.tag import Tag

router = APIRouter(prefix="/tags", tags=["Tags Categorization"])

@router.get("/")
async def get_all_tags(db: AsyncSession = Depends(get_db)):
    """ Возвращает список абсолютно всех доступных тегов/категорий в системе """
    query = select(Tag).order_by(Tag.name)                                      # Сортируем теги по алфавиту
    res = await db.execute(query)
    return res.scalars().all()                                                  # Отдаем массив тегов фронтенду
