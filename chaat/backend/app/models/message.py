from sqlalchemy import ForeignKey, DateTime, func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING, Literal
from datetime import datetime

if TYPE_CHECKING:
    from app.models.session import ChatSession

Sender = Literal["user", "bot"]

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    sender: Mapped[str] = mapped_column(String(10), nullable=False)  # 'user' | 'bot'
    text: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    session: Mapped["ChatSession"] = relationship(back_populates="messages")
