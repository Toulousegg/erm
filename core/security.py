from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from users.users_model import User
from core.dependencies import CreateSession
from fastapi.security import OAuth2PasswordBearer
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from typing import Optional
from core.exceptions import AuthenticationRequired

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

# def create_link_token(project_id: int):

#     expiration = datetime.now(timezone.utc) + timedelta(minutes=int(URL_EXPIRATION_MINUTES))
#     to_encode = {
#         "exp": expiration, 
#         "sub": str(project_id),
#         "random": random.randint(0, 999999)
#         }
#     token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return token

def create_refresh_token(user_id: int):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=int(REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode = {
        "exp": expiration,
        "sub": str(user_id)
        }
    RefreshToken = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return RefreshToken

def verify_token(request: Request, session: Session = Depends(CreateSession)) -> User:
    
    #print("COOKIES:", request.cookies)
    
    token = request.cookies.get("access_token")
    
    #print("TOKEN:", token)

    if not token:
        raise AuthenticationRequired()

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("sub") is None:
            raise AuthenticationRequired()

        id_user = int(payload.get("sub"))

    except JWTError:
        raise AuthenticationRequired()

    user = session.query(User).filter(User.id == id_user).first()

    if not user:
        raise AuthenticationRequired()

    return user

def create_verification_token(email: str, purpose: str) -> str:
    to_encode = {"sub": email, "purpose": purpose}
    expires_delta = timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_verification_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        purpose: str = payload.get("purpose")
        if email is None:
            return None
        return {"email": email, "purpose": purpose}
    except JWTError:
        return None
    
def get_user_from_token(token: str, session: Session):
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("sub") is None:
            return None

        id_user = int(payload.get("sub"))

    except Exception as e:
        #print("ERROR DECODING JWT:", e)
        return None

    user = session.query(User).filter(User.id == id_user).first()

    if not user:
        return None

    return user

def verify_admin(user: User = Depends(verify_token)):
    if user.role != "admin":
        raise HTTPException(status_code=404)

    return user