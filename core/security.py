from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker, Session
from users.users_model import User
from core.dependencies import CreateSession
from fastapi.security import OAuth2PasswordBearer
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from typing import Optional

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/home/login")



def create_token(user_id: int):

    expiration = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {
        "exp": expiration, 
        "sub": str(user_id)
        }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token



def create_refresh_token(user_id: int):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=int(REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode = {
        "exp": expiration,
        "sub": str(user_id)
        }
    RefreshToken = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return RefreshToken


def verify_token(request: Request, session: Session = Depends(CreateSession)) -> User:

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("sub") is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        id_user = int(payload.get("sub"))

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.query(User).filter(User.id == id_user).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def create_verification_token(email: str) -> str:
    to_encode = {"sub": email}
    expires_delta = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_verification_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None