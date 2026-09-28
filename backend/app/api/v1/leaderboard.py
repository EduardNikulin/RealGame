from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.session import get_db
from app.models.user import User

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard Top"])

@router.get("/")
async def get_top_players(limit: int = 10, db: AsyncSession = Depends(get_db)):
    """ Возвращает Топ-10 (или лимит) лучших игроков по общему количеству набранных очков """
    query = select(User.id, User.username, User.total_lifetime_score).where(
        User.role == "player"                                                           # Выбираем только обычных игроков
    ).order_by(User.total_lifetime_score.desc()).limit(limit)                           # Сортируем по убыванию очков
    res = await db.execute(query)
    return [{"rank": idx + 1, "id": r[0], "username": r[1], "score": r[2]} for idx, r in enumerate(res.all())]
