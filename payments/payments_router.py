import json
import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.dependencies import templates, CreateSession
from users.users_model import User
from core.security import verify_token
from payments.payments_models import Subscription, Plans
from payments.payments_services import create_subscription_service, activate_subscription, cancel_subscription, renew_subscription
from payments.payments_schema import SubscriptionCreate
from payments.webhook import verify_webhook
from moduls.moduls_models import Moduls
from utilities.limiter.limiter import limiter
from core.config import ABACATE_PAY_KEY

payments_router = APIRouter(prefix="/payments", tags=["Payments"])

MODULE_DESCRIPTIONS = {
    "inventory": "Controle materiais, ferragens e estoque da empresa com entradas, saídas e quantidades atualizadas.",
    "contacts": "Organize clientes, arquitetos, fornecedores e colaboradores em uma base centralizada.",
    "production": "Acompanhe a produção da fábrica, etapas de trabalho e prazos de entrega.",
    "projects": "Gerencie projetos por cliente, ambiente, status, arquivos e acompanhamento compartilhável.",
    "financery": "Monitore receitas, despesas, contas a pagar, contas a receber e resultado financeiro.",
    "cronograma": "Planeje a agenda semanal da equipe, tarefas e marcos importantes de entrega.",
    "notifications": "Receba avisos em tempo real sobre atividades, solicitações e mudanças relevantes.",
}

MODULE_VISUALS = {
    "inventory": "visual-inventory",
    "contacts": "visual-contacts",
    "production": "visual-production",
    "projects": "visual-projects",
    "financery": "visual-financery",
    "cronograma": "visual-cronograma",
    "notifications": "visual-notifications",
}


def build_module_cards(modules):
    cards = []

    for module in modules:
        slug = (module.slug or "").lower()
        cards.append({
            "id": module.id,
            "name": module.name,
            "slug": module.slug,
            "price": module.price,
            "price_brl": f"{module.price / 100:.2f}".replace(".", ","),
            "description": MODULE_DESCRIPTIONS.get(
                slug,
                "Ative este módulo para ampliar as ferramentas disponíveis para a sua empresa."
            ),
            "visual_class": MODULE_VISUALS.get(slug, "visual-default"),
        })

    return cards

@payments_router.post("/create_plan")
@limiter.limit("3/minute")
async def create_plan(request: Request, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    data = await request.json()
    name = data.get("name")
    amount = data.get("amount")
    external_id = data.get("external_id")
    frequency = data.get("frequency", 1) 

    if not all([name, amount, external_id]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    cycle_map = {
        1: "MONTHLY",
        12: "ANNUALLY"
    }
    abacate_cycle = cycle_map.get(frequency, "MONTHLY")

    headers = {
        "Authorization": f"Bearer {ABACATE_PAY_KEY}",
        "Content-Type": "application/json"
    }
    
    abacate_payload = {
        "externalId": external_id,
        "name": name,
        "price": amount,
        "currency": "BRL", 
        "description": f"Plano {name}",
        "cycle": abacate_cycle
    }

    try:
        response = requests.post(
            f"https://api.abacatepay.com/v2/products/create",
            json=abacate_payload,
            headers=headers
        )
        abacate_data = response.json()
        
        if response.status_code != 200 or not abacate_data.get("success"):
            error_detail = abacate_data.get("error", "Erro desconhecido no AbacatePay")
            raise HTTPException(status_code=400, detail=f"AbacatePay Error: {error_detail}")

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Erro de conexão com AbacatePay: {str(e)}")

    new_plan = Plans(
        name=name, 
        amount=amount, 
        external_id=external_id,
        frequency=frequency,
    )
    session.add(new_plan)
    session.commit()

    return {
        "status": "success", 
        "plan_id": new_plan.id,
        "abacatepay_id": abacate_data["data"]["id"]
    }
    
    
@payments_router.post("/subscription/create")
@limiter.limit("1/minute")
async def subscription_create_router(request: Request, data: SubscriptionCreate, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    try:

        result = create_subscription_service(session, user, data.module_ids)

        return {
            "status": "success",
            "subscription_id": result["subscription"].id,
            "amount": result["subscription"].amount,
            "payment_url": result["checkout_url"]
        }

    except ValueError as e:

        session.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:

        session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Internal server error."
        )

@payments_router.post("/webhook/signature")
async def abacate_pay_webhook(request: Request,session: Session = Depends(CreateSession)):

    body_bytes = await verify_webhook(request)

    try:
        data = json.loads(body_bytes)
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON"
        )

    event = data.get("event")
    payload = data.get("data") or {}
    checkout = payload.get("checkout") or {}
    payment = payload.get("payment") or {}
    subscription_data = payload.get("subscription") or {}

    
    if event == "subscription.completed":

        try:
            sub_id = int(checkout["externalId"])

        except (KeyError, ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="Invalid webhook payload"
            )

        subscription = session.query(Subscription).filter(Subscription.id == sub_id).first()

        if not subscription:
            print(f"Subscription {sub_id} not found")
            return {"status": "not_found"}

        if subscription.status in ("PAID", "ACTIVE"):
            return {
                "status": "already_processed"
            }

        subscription.is_active = True
        subscription.payment_provider_id = payment.get("id")
        subscription.provider_subscription_id = subscription_data.get("id")

        activate_subscription(session, subscription)

    elif event == "subscription.renewed":
        try:
            sub_id = int(checkout.get("externalId") or subscription_data.get("externalId"))

        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="Invalid webhook payload"
            )

        subscription = session.query(Subscription).filter(Subscription.id == sub_id).first()

        if not subscription:
            return {"status": "not_found"}

        renew_subscription(session, subscription)

    elif event == "subscription.cancelled":
        try:
            sub_id = int(checkout.get("externalId") or subscription_data.get("externalId"))

        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail="Invalid webhook payload"
            )

        subscription = session.query(Subscription).filter(Subscription.id == sub_id).first()

        if not subscription:
            return {"status": "not_found"}

        cancel_subscription(session, subscription)

    return {
        "status": "200"
    }
#VIEWS

@payments_router.get("/modules")
@limiter.limit("5/minute")
def modules_view(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    modules = session.query(Moduls).order_by(Moduls.id).all()

    return templates.TemplateResponse("payments/modules.html", {
        "request": request,
        "user": user,
        "userEmail": user.email,
        "modules": build_module_cards(modules)
    })


@payments_router.get("/moduls")
@limiter.limit("5/minute")
def moduls_view_alias(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    return RedirectResponse(url="/payments/modules", status_code=303)

@payments_router.get("/plans")
@limiter.limit("5/minute")
def plans_view(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)): 
    """Renderiza la página de selección de planes."""
    plans = session.query(Plans).order_by(Plans.id).all()
     
    return templates.TemplateResponse("plans/plans.html", {
        "request": request,
        "plans": plans,
        "user": user,
        "userEmail": user.email,
        "amount": plans[0].amount if plans else 0,
        "plan_basic_id": plans[0].id if len(plans) > 0 else None,
        "plan_premium_id": plans[1].id if len(plans) > 1 else None,
        "plan_enterprise_id": plans[2].id if len(plans) > 2 else None,
        "plan_annual_id": plans[3].id if len(plans) > 3 else None,
        "plan_basic_price": plans[0].amount/100 if len(plans) > 0 else 0,
        "plan_premium_price": plans[1].amount/100 if len(plans) > 1 else 0,
        "plan_enterprise_price": plans[2].amount/100 if len(plans) > 2 else 0,
        "plan_annual_price": plans[3].amount/100 if len(plans) > 3 else 0,
        "descuento": round((plans[2].amount * 12) - plans[3].amount, 2) / 100 if len(plans) > 3 else 0 #dividir entre 100 por lo centavos, bruh
    })
    
@payments_router.get("/success")
@limiter.limit("5/minute")
def success_view(request: Request, user: User = Depends(verify_token)):
    return templates.TemplateResponse("payments/pay_sucess.html", {
        "request": request,
        "user": user
    })
    
@payments_router.get("/pending")
@limiter.limit("5/minute")
def pending_view(request: Request, user: User = Depends(verify_token)):
    return templates.TemplateResponse("payments/pay_pending.html", {
        "request": request,
        "user": user
    })
    
@payments_router.get("/failure")
@limiter.limit("5/minute")
def failure_view(request: Request, user: User = Depends(verify_token)):
    return templates.TemplateResponse("payments/pay_fail.html", {
        "request": request,
        "user": user
    })
