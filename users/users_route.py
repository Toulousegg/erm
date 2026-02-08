from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from users.users_model import User
from users.users_schemas import UserSchema, UserLoginSchema
from core.security import bcrypt_context, verify_token
from core.dependencies import CreateSession
from core.security import create_token, create_refresh_token
from fastapi.security import OAuth2PasswordRequestForm

def authuser(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email==email).first()
    if not user:
        return None

    elif not bcrypt_context.verify(password, user.password):
        return None

    return user

home_router = APIRouter(prefix="/home", tags=["home"])


@home_router.post("/login")
def authenticate_user(userloginschema: UserLoginSchema, Session: Session = Depends(CreateSession)):
    user = authuser(userloginschema.username, userloginschema.password, Session)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    else:
        access_token = create_token(user.id)
        refresh_token = create_refresh_token(user.id) 
        
        return {"message": "User authenticated successfully" 
                , "access_token": access_token
                , "refresh_token": refresh_token
                , "token_type": "bearer"
                }


@home_router.post("/login-form")
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(CreateSession)
):
    user = authuser(form_data.username, form_data.password, session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token = create_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@home_router.get("/refresh")
def refresh_token(user: User = Depends(verify_token)):
    access_token = create_token(user.id)
    return {
        "access_token": access_token, 
        "token_type": "bearer"
     }
    
    
@home_router.post("/signup")
def create_user(userschema: UserSchema, session: Session = Depends(CreateSession)):
    user = session.query(User).filter((User.email==userschema.email) | (User.username==userschema.username)).first()
    try:
        if user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        
        if len(userschema.password) < 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters long")
        

        password = bcrypt_context.hash(userschema.password)
        new_user = User(
            username=userschema.username,
            email=userschema.email,
            password=password,
            fullname=userschema.fullname
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"message": "User created successfully"}
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=401, detail=f"Error creating user: {str(e)}")
    
