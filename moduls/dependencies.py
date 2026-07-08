#esto es para colocar las dependencias en los router y no tener que repetir logica a cada rato
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.security import CreateSession
from core.security import verify_token
from moduls.moduls_services import has_module

def get_company_id(user=Depends(verify_token)):
    return user.company_id

def require_module(slug: str):
    def dependency(company_id: int = Depends(get_company_id), session: Session = Depends(CreateSession)):

        allow = has_module(session, company_id, slug)

        if not allow:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Module '{slug}' not available for this company"
            )

        return True

    return dependency