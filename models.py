# -------------------------------------------------------------------------
# models.py - SQLAlchemy ORM Models
# -------------------------------------------------------------------------
import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class RoleEnum(str, enum.Enum):
    user = "user"
    assistant = "assistant"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_login = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    # ... other user fields

class Session(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False, default="New Chat")
    created_at = Column(TIMESTAMP, server_default=func.now())
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    session = relationship("Session", back_populates="messages")