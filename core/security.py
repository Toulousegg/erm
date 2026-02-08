from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import os
from passlib.context import CryptContext
from sqlalchemy.orm import sessionmaker, Session
from users.users_model import User
from core.dependencies import CreateSession
from fastapi.security import OAuth2PasswordBearer

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/home/login-form")

def create_token(user_id: int):

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expiration, 
        "sub": str(user_id)
        }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def create_refresh_token(user_id: int):
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))
    expiration = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expiration,
        "sub": str(user_id)
        }
    RefreshToken = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return RefreshToken

#esta funcion va a intentar verificar el token, si no puede, lanza una excepcion
def verify_token(token: str = Depends(oauth2_schema), session: Session = Depends(CreateSession)) -> User: #el -> sirve para decir que tipo de dato va a retornar la funcion
    try:        
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])

        if payload.get("sub") is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token, verify token")
        
        id_user = int(payload.get("sub"))

    except JWTError as error: #aqui capturo cualquier error de verificacion del token y poder manejarlo
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token, verify token")
    
    user = session.query(User).filter(User.id == id_user).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user