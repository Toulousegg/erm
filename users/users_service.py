from fastapi import HTTPException
from sqlalchemy.orm import Session
from users.users_model import User
from core.security import bcrypt_context
import random
from datetime import datetime, timedelta, timezone
from core.email_service import send_verification_email
from core.config import VERIFICATION_TOKEN_EXPIRE_MINUTES
from users.users_model import Company
from io import BytesIO
import barcode
from barcode.writer import ImageWriter

def authuser(identifier: str, password: str, session: Session):
    user = session.query(User).filter((User.username == identifier) | (User.email == identifier)).first()

    if not user:
        return None

    if not bcrypt_context.verify(password, user.password):
        return None

    return user

async def generate_and_send_verification_code(user: User, session: Session):
    code = str(random.randint(100000, 999999))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES)
    user.verification_code = code
    user.verification_code_expires_at = expires_at
    session.add(user)
    session.commit()
    session.refresh(user)
    await send_verification_email(user.email, code)
    return user

def verify_user_email(user: User, code: str, session: Session, data: dict):
    
    if not user.verification_code or user.verification_code != code:
        return False
    if user.verification_code_expires_at < datetime.now(timezone.utc):
        return False
    
    purpose = data.get("purpose")
    
    if purpose == "password_reset":
        user.password = user.temp_password
        user.verification_code = None
        user.verification_code_expires_at = None
        user.temp_password = None
        session.commit()
        session.refresh(user)

    
    if purpose == "email_verification":
        user.is_verified = 1
        user.verification_code = None
        user.verification_code_expires_at = None
        session.add(user)
        session.commit()
        session.refresh(user)
    
    return True

def create_company(session, company_name, legal_name, tax_id, email):
    company = session.query(Company).filter((Company.legal_name == legal_name) | (Company.tax_id == tax_id) | (Company.email == email)).first()
    
    if company:
        raise HTTPException(status_code=400, detail="Company already exists")

    company_data = Company(
        name=company_name,
        legal_name=legal_name,
        tax_id=tax_id,
        email=email,
    )
    
    
    session.add(company_data)
    session.flush()
    
    return company_data