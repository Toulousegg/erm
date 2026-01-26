from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import os
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
