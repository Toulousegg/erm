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
from moduls.moduls_services import build_module_cards
from utilities.limiter.limiter import limiter
from core.config import ABACATE_PAY_KEY

payments_router = APIRouter(prefix="/payments", tags=["Payments"])

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
