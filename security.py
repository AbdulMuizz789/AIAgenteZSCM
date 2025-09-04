from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from fastapi import Header, Depends
from models import User
from sqlalchemy.orm import Session

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv('SECRET_KEY'), algorithm=os.getenv('ALGORITHM'))
    return encoded_jwt

def verify_token(token: str):
    credentials_exception = Exception("Could not validate credentials")
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except JWTError:
        raise credentials_exception
    
def get_current_user(authorization: str = Header('Authorization')) -> User:
    if authorization is None or not authorization.startswith("Bearer "):
        raise Exception("Could not validate credentials")
    token = authorization.split(" ")[1]
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise Exception("Could not validate credentials")
    return user