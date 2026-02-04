from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.session import ChatSession
from app.models.message import Message
from app.schemas.chat import SessionCreateOut, ChatMessageIn, ChatMessageOut, HistoryOut, MessageOut
from app.services.bot import get_bot_reply

router = APIRouter()

@router.post("/session", response_model=SessionCreateOut, status_code=status.HTTP_201_CREATED)
async def create_session(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    s = ChatSession(user_id=user.id)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return SessionCreateOut(session_id=s.id)

@router.post("/message", response_model=ChatMessageOut)
async def send_message(
    payload: ChatMessageIn,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    res = await db.execute(select(ChatSession).where(ChatSession.id == payload.session_id))
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")

    bot_text = get_bot_reply(payload.text)

    user_msg = Message(session_id=session.id, sender="user", text=payload.text.strip())
    bot_msg = Message(session_id=session.id, sender="bot", text=bot_text)
    db.add_all([user_msg, bot_msg])
    await db.commit()

    return ChatMessageOut(session_id=session.id, user_text=user_msg.text, bot_text=bot_text)

@router.get("/history/{session_id}", response_model=HistoryOut)
async def get_history(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    res = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
        .options(selectinload(ChatSession.messages))
    )
    session = res.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your session")

    msgs = sorted(session.messages, key=lambda m: m.created_at)
    out = [MessageOut(id=m.id, sender=m.sender, text=m.text, created_at=m.created_at) for m in msgs]
    return HistoryOut(session_id=session.id, messages=out)
