import models
import schemas
from sqlalchemy.orm import Session
import uuid
from typing import Optional
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user and verify_password(password, db_user.hashed_password):
        return db_user

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password = get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_sessions(db: Session, user_id: uuid.UUID) -> list[models.Session]:
    return db.query(models.Session).filter(models.Session.user_id == user_id).all()

def get_session(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> list[models.Session]:
    return db.query(models.Session).filter(models.Session.id == session_id, models.Session.user_id == user_id).first()

def create_session(db: Session, session: schemas.SessionCreate, user_id: uuid.UUID) -> models.Session:
    new_session = models.Session(
        user_id=user_id,
        title=session.title or "New Chat"
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def update_session_title(db: Session, session_id: uuid.UUID, user_id: uuid.UUID, title: str) -> Optional[Session]:
    pass

def delete_session(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
    pass

def create_message(db: Session, role: str, session_id: uuid.UUID, content: str, user_id: uuid.UUID):
    user_message_db = models.Message(
        session_id=session_id,
        role=role,
        content=content
    )
    db.add(user_message_db)
    db.commit()

def get_messages(db: Session, session_id: uuid.UUID, user_id: uuid.UUID) -> list[models.Message]:
    return db.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.created_at).all()

