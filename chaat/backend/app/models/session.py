from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.message import Message

class ChatSession(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="sessions")

    messages: Mapped[List["Message"]] = relationship(back_populates="session", cascade="all, delete-orphan")
