from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import JWTError, jwt
import os
from fastapi import Header, Depends, HTTPException, status
from models import User
from sqlalchemy.orm import Session
from database import get_db

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes

def create_access_token(data: dict, expires_delta: timedelta):
    expire = datetime.utcnow() + expires_delta
    data['exp'] = expire
    encoded_jwt = jwt.encode(data, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    return encoded_jwt

def verify_token(token: str):
    credentials_exception = Exception("Could not validate credentials,")
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception
    
def get_current_user(
    db: Session = Depends(get_db),
    authorization: str = Header(None, alias="Authorization")
) -> User:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials, no proper token provided"
        )
    token = authorization.split(" ")[1]
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials, user not found"
        )
    return user