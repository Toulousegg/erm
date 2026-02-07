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

#esta funcion va a intentar verificar el token, si no puede, lanza una excepcion
def verify_token(token: str = Depends(oauth2_schema), session: Session = Depends(CreateSession)):
    try:        
        decode = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        id_user = decode.get("sub")
        print(f"Decoded token user id: {id_user}")

    except JWTError as error: #aqui capturo cualquier error de verificacion del token y poder manejarlo
        print(f"Token verification error: {error}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token, verify token")
    
    user = session.query(User).filter(User.id == decode.get("sub")).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user