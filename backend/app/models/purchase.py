import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import Numeric, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base


class UserPurchase(Base):
    __tablename__ = "user_purchases"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    
    # Кто купил (при удалении пользователя удалится и запись о покупке)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Какой квест купил (при удалении квеста удалится и запись)
    quest_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quests.id", ondelete="CASCADE"), 
        nullable=False
    )
    
    # Сколько фактически заплатил (на случай, если цена квеста изменится в будущем)
    paid_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), 
        nullable=False
    )
    
    # Когда была совершена покупка
    purchased_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
