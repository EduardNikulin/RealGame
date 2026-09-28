from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.api.v1.deps import get_current_user
from app.database.session import get_db
from app.models.progress import UserProgress
from app.models.user import User

router = APIRouter(prefix="/user", tags=["User Profile"])

@router.get("/progress")
async def get_user_game_history(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """ Возвращает историю всех завершенных игроком квестов и его финальные очки """
    query = select(UserProgress).where(
        UserProgress.user_id == current_user.id,
        UserProgress.status == "completed"                                      # Выбираем строго пройденные квесты
    ).order_by(UserProgress.finished_at.desc())                                 # Сортируем: сначала новые
    res = await db.execute(query)
    return res.scalars().all()                                                  # Отдаем историю прохождений
