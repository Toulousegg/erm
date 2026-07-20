from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from moduls.moduls_services import get_company_modules
from core.security import verify_token
from core.dependencies import CreateSession, templates
from users.users_model import User

modules_router = APIRouter(prefix="/modules", tags=["Modules"])


@modules_router.get("/company")
def company_modules(request: Request, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    if user and user.company_id:
        modules = [
    {
        "id": module.id,
        "name": module.name,
        "route": module.module_route,
        "icon": module.icon
    }
    for module in get_company_modules(session, user.company_id)
]
    
    return templates.TemplateResponse(
        "aside.html",
        {
            "request": request,
            "modules": modules
        }
    )