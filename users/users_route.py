from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from users.users_model import User
from core.security import bcrypt_context, verify_token
from core.dependencies import CreateSession
from core.security import create_token, create_refresh_token
from fastapi.security import OAuth2PasswordRequestForm
from users.users_service import authuser
from core.dependencies import templates

home_router = APIRouter(prefix="/home", tags=["home"])


@home_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(CreateSession)
):
    user = authuser(form_data.username, form_data.password, session)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    access_token = create_token(user.id)

    response = RedirectResponse(url="/inv/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax"
    )

    return response


@home_router.get("/refresh")
def refresh_token(user: User = Depends(verify_token)):
    access_token = create_token(user.id)
    return {
        "access_token": access_token, 
        "token_type": "bearer"
     }
    
    
@home_router.post("/signup")
def create_user(request: Request, session: Session = Depends(CreateSession), fullname: str = Form(...), username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    user = session.query(User).filter((User.email==email) | (User.username==username)).first()
    
    try:
        if user:
            return templates.TemplateResponse("home/signup.html", {
                "message": "User with this email or username already exists",
                "request": request})
        
        if len(password) < 8:
            return templates.TemplateResponse("home/signup.html", {
                "message": "Password must be at least 8 characters long",
                "request": request})
            

        password = bcrypt_context.hash(password)
        new_user = User(
            username=username,
            email=email,
            password=password,
            fullname=fullname
        )
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return templates.TemplateResponse("home/signup.html", {
        "request": request})
    
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=401, detail=f"Error creating user: {str(e)}")


#VIEWS

 
@home_router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("home/login.html", {"request": request})

@home_router.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse("home/signup.html", {
        "request": request})