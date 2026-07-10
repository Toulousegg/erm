from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session
from core.dependencies import templates, CreateSession
from users.users_model import User
from payments.payments_models import Plans
from core.security import verify_admin
from admin.admin_services import create_plan, delete_plan_abacatepay, create_module, list_modules
from core.config import ABACATE_PAY_KEY
from utilities.limiter.limiter import limiter

admin_router = APIRouter(prefix="/admin", tags=["admin"])#, include_in_schema=False)

@admin_router.post("/create-plan")
@limiter.limit("5/minute")
def create_plan_route(request: Request, payload: dict, session: Session = Depends(CreateSession), user: User = Depends(verify_admin)):
    create_plan(user, name=payload["name"], amount=payload["amount"], frequency=payload["frequency"], session=session)
    return {"status": "created"}

@admin_router.post("/create-module")
@limiter.limit("10/minute")
def create_module_route(request: Request, name: str = Form(...), slug: str = Form(...), description: str = Form(...), price: int = Form(...), image: UploadFile = File(...), session: Session = Depends(CreateSession), user: User = Depends(verify_admin)):
    try:

        module = create_module(
            name=name,
            slug=slug,
            price=price,
            description=description,
            image=image,
            session=session
        )

        return {
            "status": "created",
            "module_id": module.id
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@admin_router.post("/update-plan/{plan_id}")
@limiter.limit("1/minute")
def update_plan_route(request: Request, plan_id: int, payload: dict, session: Session = Depends(CreateSession), user: User = Depends(verify_admin)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Unauthorized")

    plan = session.query(Plans).filter(Plans.id == plan_id).first()

    if not plan:
        raise HTTPException(status_code=404)

    if "name" in payload:
        plan.name = payload["name"]

    if "amount" in payload:
        plan.amount = payload["amount"]

    if "frequency" in payload:
        plan.frequency = payload["frequency"]

    session.commit()

    return {"status": "updated"}

@admin_router.delete("/delete-plan")
def delete_plan_route(external_id: str, session: Session = Depends(CreateSession), user: User = Depends(verify_admin)):
    delete_plan_abacatepay(external_id, ABACATE_PAY_KEY, user, session)
    return {"status": "deleted"}

#VIEWS

@admin_router.get("")
@limiter.limit("5/minute")
def create_plan_page(request: Request, user: User = Depends(verify_admin), session: Session = Depends(CreateSession)):
    
    if user.role != "admin":
        return templates.TemplateResponse("responses/404.html", {
            "request": request
        })
    
    else:
        plans = session.query(Plans).all()
        modules = list_modules(session)
        
        return templates.TemplateResponse("admin/admin.html", {
            "request": request,
            "user": user,
            "planes": [
                {
                    "id": plan.id,
                    "name": plan.name.value,
                    "amount": plan.amount,
                    "frequency": plan.frequency
                    } 
                
                for plan in plans
                ],
            "modules": [
                {
                    "id": module.id,
                    "name": module.name,
                    "slug": module.slug,
                    "price": module.price,
                    "description": module.description,
                    "price_brl": module.price / 100,
                    "icon_url": module.icon_url
                    }

                for module in modules
                ]
            })
