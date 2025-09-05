# -------------------------------------------------------------------------
# schemas.py - Pydantic Models for API validation
# -------------------------------------------------------------------------
import uuid
from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    created_at: datetime
    last_login: datetime | None = None
    class Config:
        orm_mode = True

class Message(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime
    class Config:
        orm_mode = True

class Session(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    messages: list[Message] = []
    class Config:
        orm_mode = True

class SessionCreate(BaseModel):
    title: str | None = None

class ChatRequest(BaseModel):
    session_id: uuid.UUID
    prompt: str
    provider: str
    model: str

class SessionUpdate(BaseModel):
    title: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str