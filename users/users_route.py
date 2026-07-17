from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from users.users_model import User, Company, CompanyJoinRequest
from notification.notification_services import manager, create_notification, notify_company_join, ensure_company_assignment_reminder
from core.security import bcrypt_context, verify_token
from core.dependencies import CreateSession
from core.security import create_token, create_verification_token, verify_verification_token, create_refresh_token
from fastapi.security import OAuth2PasswordRequestForm
from users.users_service import authuser, generate_and_send_verification_code, verify_user_email, create_company
from core.dependencies import templates
from core.config import SECRET_KEY, ALGORITHM
from jose import jwt
from utilities.limiter.limiter import limiter
from core.email_service import send_employee_barcode_to_owner
from core.barcode_service import generate_code128, generate_barcode_image
from fastapi.responses import StreamingResponse

home_router = APIRouter(prefix="/home", tags=["home"])


def next_onboarding_url(user: User) -> str:
    if not user.company_id or not user.company:
        return "/home/create-company"

    subscription = user.company.company_subscription

    if not subscription or not subscription.is_active:
        return "/payments/modules"

    return "/inv/dashboard"


def set_auth_cookies(response: RedirectResponse, user_id: int):
    access_token = create_token(user_id)
    refresh_token = create_refresh_token(user_id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False, #mantener este valor en false en desarrollo y true en produccion porque puede hacer que la cookie no se guarde
        samesite="lax"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False, #mantener este valor en false en desarrollo y true en produccion porque puede hacer que la cookie no se guarde
        samesite="lax"
    )

    return response


@home_router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(CreateSession)):
    user = authuser(form_data.username, form_data.password, session)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    if not user.is_verified:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "email": user.email, 
            "message": "Please verify your email address before logging in."
        })

    await ensure_company_assignment_reminder(user, session)

    response = RedirectResponse(url=next_onboarding_url(user), status_code=303)
    
    if not user.barcode:
        try:
            if user.company:
                user.barcode = generate_code128(12)
                session.commit()
                await send_employee_barcode_to_owner(user.company.owner.email, user.fullname, user.username, user.barcode)
                return set_auth_cookies(RedirectResponse(url="/home/barcode/", status_code=303), user.id)

        except Exception as e:
            print("Error sending barcode email:", e)
            return set_auth_cookies(RedirectResponse(url=next_onboarding_url(user), status_code=303), user.id)

    return set_auth_cookies(response, user.id)
    

@home_router.post("/signup")
@limiter.limit("2/minute")
async def create_user(request: Request, session: Session = Depends(CreateSession), company: str = Form(None), fullname: str = Form(...), username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    
    user = session.query(User).filter((User.email==email) | (User.username==username) | (User.fullname==fullname)).first()
    
    try:
        if user:
            return templates.TemplateResponse("home/signup.html", {
                "message": "User already exists",
                "request": request})
        
        if len(password) < 8:
            return templates.TemplateResponse("home/signup.html", {
                "message": "Password must be at least 8 characters long",
                "request": request})
            
        password = bcrypt_context.hash(password)

        company_obj = session.query(Company).filter(Company.name == company).first()

        new_user = User(
            username=username,
            email=email,
            password=password,
            fullname=fullname,
        )

        session.add(new_user)
        session.flush()
        session.refresh(new_user)

        verification_jwt = create_verification_token(new_user.email, "email_verification")

        if company_obj:
            join_request = CompanyJoinRequest(
            user_id=new_user.id,
            company_id=company_obj.id,
            )
            
            session.add(join_request)
            session.commit()

            await notify_company_join(join_request.id, session, new_user)

            await create_notification(company_obj.owner_id, company_obj.id, join_request.message, session)
            
            owner_id = company_obj.owner_id
            
            try:
                await manager.send_to_user(owner_id, join_request.message)
        
            except:
                pass
            
        else:
            pass

        await generate_and_send_verification_code(new_user, session)

        user_email = new_user.email

        return templates.TemplateResponse("home/verify_email.html", {
            "request": request,
            "verification_jwt": verification_jwt,
            "message": "A verification code has been sent to your email.",
            "user_email": user_email
        })
    
    except Exception as e:
        session.rollback()
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


@home_router.post("/verify-email")
@limiter.limit("5/minute")
async def verify_email(request: Request,session: Session = Depends(CreateSession), code: str = Form(...), verification_jwt: str = Form(...)):

    data = verify_verification_token(verification_jwt)

    if not data:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "message": "No data found.",
            "verification_jwt": verification_jwt 
        })

    email = data.get("email")
    
    purpose = data.get("purpose")
    user = session.query(User).filter(User.email == email).first()
    if not user:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "message": "User not found.",
            "verification_jwt": verification_jwt
        })
    
    if verify_user_email(user, code, session, {"email": email, "purpose": purpose}):
        if purpose == "email_verification":
            response = RedirectResponse(url=next_onboarding_url(user), status_code=status.HTTP_303_SEE_OTHER)
            
            return set_auth_cookies(response, user.id)

        return RedirectResponse(url="/home/login", status_code=status.HTTP_303_SEE_OTHER)
    
    else:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "email": email, 
            "verification_jwt": verification_jwt,
            "message": "Invalid verification code."
        })


@home_router.post("/resend-verification-email")
@limiter.limit("2/minute")
async def resend_verification_email(request: Request, session: Session = Depends(CreateSession), verification_jwt: str = Form(...)):
    data = verify_verification_token(verification_jwt)
    
    purpose = data.get("purpose")
    
    email = data.get("email")
    if not email:
        return templates.TemplateResponse("home/login_email.html", {
            "request": request, 
            "message": "Invalid or expired verification link. Please try logging in again."
        })

    user = session.query(User).filter(User.email == email).first()
    if not user:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "message": "User not found. Please register or log in."
        })
    
    if user.is_verified:

        return RedirectResponse(url="/home/login", status_code=status.HTTP_303_SEE_OTHER)

    await generate_and_send_verification_code(user, session)
    
    new_verification_jwt = create_verification_token(user.email, "email_verification")

    return templates.TemplateResponse("home/verify_email.html", {
        "request": request, 
        "email": user.email,
        "verification_jwt": new_verification_jwt,
        "message": "A new verification code has been sent to your email."
    })

@home_router.post("/create-company")
@limiter.limit("2/minute")
def create_company_router(request: Request, session: Session = Depends(CreateSession), company_name: str = Form(...), legal_name: str = Form(...), tax_id: str = Form(...), email: str = Form(...)):
    
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = int(payload.get("sub"))

    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.company:
        raise HTTPException(status_code=401, detail="Invalid request")
    
    company = create_company(session, company_name, legal_name, tax_id, email)
    
    company.owner_id = user.id
    
    user.company_id = company.id
    
    user.role = "owner"

    session.commit()

    return RedirectResponse(url="/payments/modules", status_code=303)

@home_router.post("/forgot-password")
async def forgot_password(request: Request, password: str = Form(...), confirm_password: str = Form(...), session: Session = Depends(CreateSession), username: str = Form(...)):
    user = session.query(User).filter((User.email==username) | (User.username==username) | (User.fullname==username)).first()

    if not user:
        return templates.TemplateResponse("home/forgot_password.html", {
            "request": request,
            "message": "User not found."
        })
    
    if password != confirm_password:
        return templates.TemplateResponse("home/forgot_password.html", {
            "request": request,
            "message": "Passwords do not match."
        })
        
    if len(password) < 8:
        return templates.TemplateResponse("home/forgot_password.html", {
            "request": request,
            "message": "Password must be at least 8 characters long."
        })  
        
    user.temp_password = bcrypt_context.hash(password)
    session.commit()
        
    verification_code = await generate_and_send_verification_code(user, session)
    
    if verification_code:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request,
            "verification_jwt": create_verification_token(user.email, "password_reset"),
            "message": "A verification code has been sent to your email. Please verify to reset your password."
        })

@home_router.post("/verify-email-password")
@limiter.limit("5/minute")
async def verify_email_password(request: Request, code: str = Form(...), verification_jwt: str = Form(...), session: Session = Depends(CreateSession)):
    data = verify_verification_token(verification_jwt)

    if not data:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "message": "No email found.",
            "verification_jwt": verification_jwt 
        })

    email = data.get("email")
    
    purpose = data.get("purpose")

    user = session.query(User).filter(User.email == email).first()
    
    if not user:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "message": "User not found.",
            "verification_jwt": verification_jwt
        })
    
    if verify_user_email(user, code, session, {"email": email, "purpose": purpose}):
        return RedirectResponse(url="/home/login", status_code=status.HTTP_303_SEE_OTHER)
    
    else:
        return templates.TemplateResponse("home/verify_email.html", {
            "request": request, 
            "email": email, 
            "verification_jwt": verification_jwt,
            "message": "Invalid verification code."
        })
#VIEWS
@home_router.get("/verify-email-password")
def verify_email_password_view(request: Request, verification_jwt: str):
    return templates.TemplateResponse("home/verify_email.html", {
        "request": request,
        "verification_jwt": verification_jwt
    })

@home_router.get("/forgot-password")
def forgot_password_view(request: Request):
    return templates.TemplateResponse("home/forgot_password.html", {
        "request": request
    })

@home_router.get("/create_company")
def create_company_alias():
    return RedirectResponse(url="/home/create-company", status_code=303)

@home_router.post("/refresh")
def refresh_token(request: Request, session: Session = Depends(CreateSession)):
    
    refresh_token_cookie = request.cookies.get("refresh_token")
    
    if not refresh_token_cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(refresh_token_cookie, SECRET_KEY, algorithms=[ALGORITHM])
        
    except:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    sub = payload.get("sub")

    if not sub:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = int(sub)
    
    user = session.query(User).filter(User.id == user_id).first() 
    
    if not user: 
        raise HTTPException(status_code=401, detail="User not found")
    
    new_access = create_token(user_id)
    
    response = JSONResponse(content={"message": "refreshed"})
    
    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=False, #mantener este valor en false en desarrollo y true en produccion porque puede hacer que la cookie no se guarde
        samesite="lax"
    )
     
    return response

@home_router.get("/login")
def login_view(request: Request):
    return templates.TemplateResponse("home/login.html", {
        "request": request
    })
    
@home_router.get("/signup")
def signup_view(request: Request):
    return templates.TemplateResponse("home/signup.html", {
        "request": request
    })

@home_router.get("/barcode")
def barcode_page(request: Request, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    user = session.query(User).filter(User.id == user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(
        "home/barcode.html",
        {
            "request": request,
            "user": user
        }
    )
    
@home_router.get("/barcode/view")
def get_user_barcode(session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    user = session.query(User).filter(User.id == user.id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.barcode:
        raise HTTPException(status_code=404, detail="User has no barcode")

    barcode_buffer = generate_barcode_image(user.barcode)

    return StreamingResponse(
        barcode_buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="barcode_{user.username}.png"'
        }
    )