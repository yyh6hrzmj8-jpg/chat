from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

class SessionCreateOut(BaseModel):
    session_id: int

class ChatMessageIn(BaseModel):
    session_id: int
    text: str = Field(min_length=1, max_length=2000)

class ChatMessageOut(BaseModel):
    session_id: int
    user_text: str
    bot_text: str

class MessageOut(BaseModel):
    id: int
    sender: Literal["user","bot"]
    text: str
    created_at: datetime

class HistoryOut(BaseModel):
    session_id: int
    messages: List[MessageOut]
