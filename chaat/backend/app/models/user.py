from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.session import ChatSession

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    sessions: Mapped[List["ChatSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
