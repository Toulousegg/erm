from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from users.users_model import User
from users.users_schemas import UserSchema, UserLoginSchema
from core.security import bcrypt_context
from core.dependencies import CreateSession
from core.security import create_token
import os

def authuser(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email==email).first()
    if not user:
        return None

    elif not bcrypt_context.verify(password, user.password):
        return None

    return user

def createToken(user_id: int, token_duration: dotenv.get("TOKEN):
    return create_token(user_id, token_duration)

home_router = APIRouter(prefix="/home", tags=["home"])


@home_router.post("/login")
def authenticate_user(userloginschema: UserLoginSchema, Session: Session = Depends(CreateSession)):
    user = authuser(userloginschema.email, userloginschema.password, Session)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    else:
        access_token = create_token(user.id)
        
        
        print(f"Token created successfully: {access_token}")
        return {"message": "User authenticated successfully" 
                , "access_token": access_token
                , "token_type": "bearer"
                }
    
    
@home_router.post("/singup")
def create_user(userschema: UserSchema, Session: Session = Depends(CreateSession)):
    user = Session.query(User).filter((User.email==userschema.email) | (User.username==userschema.username)).first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    
    else:
        password = bcrypt_context.hash(userschema.password)
        new_user = User(
            username=userschema.username,
            email=userschema.email,
            password=password,
            fullname=userschema.fullname
        )
        Session.add(new_user)
        Session.commit()
        Session.refresh(new_user)
        print(f"User created successfully: {new_user}")
        return {"message": "User created successfully"}
