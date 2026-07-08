from fastapi import APIRouter, Depends, Request, HTTPException, Body, Query
from fastapi.responses import RedirectResponse
from math import ceil
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates
from core.security import verify_token
from users.users_model import User
from financery.financery_services import (
    add_sell,
    kdis_calculate,
    financial_transaction_charts,
    get_pending_debts,
    get_pending_receivables,
    add_debts,
    to_receive,
    pay_debt,
    pay_receivable,
    delete_payment,
    delete_receivable,
    edit_payment,
    edit_receivable,
    is_owner
)
from financery.financery_models import Sells, Receivable, Debt
from financery.financery_schema import SellsSchema, DebtCreateSchema, ReceivableCreate
from datetime import date
from utilities.limiter.limiter import limiter
from moduls.dependencies import require_module

financery_router = APIRouter(prefix="/financery", tags=["financery"])


@financery_router.post("/sell", dependencies=[Depends(require_module("financery"))])
@limiter.limit("5/minute")
def add_sell_endpoint(request: Request, data: SellsSchema, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    isowner = is_owner(user)
    
    if isowner:
        add_sell(user, session, data)
        return RedirectResponse("/financery/dashboard", status_code=303)
    
    else:
        return ValueError('No Owner')


@financery_router.delete("/sell/{sell_id}", dependencies=[Depends(require_module("financery"))])
@limiter.limit("5/minute")
def delete_sell_endpoint(request: Request, sell_id: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    isowner = is_owner(user)
    
    if isowner:
        sell = session.query(Sells).filter(Sells.id == sell_id, Sells.company_id == user.company_id).first()
        if not sell:
            raise HTTPException(status_code=404, detail="Sell not found")
        session.delete(sell)
        session.commit()
        return {"message": "Sell deleted"}
    
    else:
        return ValueError('No Owner')


@financery_router.post("/dashboard/debt", dependencies=[Depends(require_module("financery"))])
@limiter.limit("8/minute")
def create_debt(request: Request, data: DebtCreateSchema, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    isowner = is_owner(user)
    
    if isowner:
        add_debts(user, session, data)
        return {"message": "Debt created"}
    
    else:
        return ValueError('No Owner')


@financery_router.post("/dashboard/receivable", dependencies=[Depends(require_module("financery"))])
@limiter.limit("8/minute")
def create_receivable(request: Request, data: ReceivableCreate, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    isowner = is_owner(user)
    
    if isowner:
        to_receive(user, session, data)
        return {"message": "Receivable created"}
    
    else:
        return ValueError('No Owner')


@financery_router.post("/dashboard/payment/{payment_id}/pay", dependencies=[Depends(require_module("financery"))])
@limiter.limit("8/minute")
def pay_debt_endpoint(request: Request, payment_id: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    isowner = is_owner(user)
    
    if isowner:
        pay_debt(user, session, payment_id)
        return {"message": "Payment marked as paid"}
    
    else:
        return ValueError('No Owner')


@financery_router.post("/dashboard/receivable/{receivable_id}/pay", dependencies=[Depends(require_module("financery"))])
@limiter.limit("8/minute")
def pay_receivable_endpoint(request: Request, receivable_id: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    isowner = is_owner(user)
    
    if isowner:
        pay_receivable(user, session, receivable_id)
        return {"message": "Receivable marked as paid"}
    
    else:
        return ValueError('No Owner')


@financery_router.delete("/dashboard/payment/{payment_id}", dependencies=[Depends(require_module("financery"))])
@limiter.limit("8/minute")
def delete_payment_endpoint(request: Request, payment_id: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    isowner = is_owner(user)
    
    if isowner:
        delete_payment(user, session, payment_id)
        return {"message": "Pending payment deleted"}
    
    else:
        return ValueError('No Owner')


@financery_router.delete("/dashboard/receivable/{receivable_id}", dependencies=[Depends(require_module("financery"))])
@limiter.limit("8/minute")
def delete_receivable_endpoint(request: Request, receivable_id: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    isowner = is_owner(user)
    
    if isowner:
        delete_receivable(user, session, receivable_id)
        return {"message": "Receivable deleted"}
    
    else:
        return ValueError('No Owner')


@financery_router.put("/dashboard/payment/{payment_id}", dependencies=[Depends(require_module("financery"))])
@limiter.limit("8/minute")
def edit_payment_endpoint(request: Request, payment_id: int, data: dict = Body(...), user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    isowner = is_owner(user)
    
    if isowner:
        edit_payment(user, session, payment_id, data)
        return {"message": "Pending payment updated"}
    
    else:
        return ValueError('No Owner')


@financery_router.put("/dashboard/receivable/{receivable_id}", dependencies=[Depends(require_module("financery"))])
@limiter.limit("8/minute")
def edit_receivable_endpoint(request: Request, receivable_id: int, data: dict = Body(...), user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    isowner = is_owner(user)
    
    if isowner:
        edit_receivable(user, session, receivable_id, data)
        return {"message": "Receivable updated"}
    
    else:
        return ValueError('No Owner')
    
@financery_router.get("/users/search", dependencies=[Depends(require_module("financery"))]) #esta funcion es para el autocomplete del input de carpintero en el html
def search_users_route(request: Request, username: str, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    users = session.query(User).filter((User.company_id == user.company_id), User.username.ilike(f"%{username}%") | (User.fullname.ilike(f"%{username}%"))).all()

    return [
        {"id": user.id, "name": user.username}
        for user in users
    ]

#VIEWS

@financery_router.get("/dashboard", dependencies=[Depends(require_module("financery"))])
def show_sell(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession), page_sells: int = Query(1, ge=1), page_debts: int = Query(1, ge=1), page_receivables: int = Query(1, ge=1)):
    
    isowner = is_owner(user)
    
    if isowner:
        
        PER_PAGE = 10
        base_sells_query = session.query(Sells).filter(Sells.company_id == user.company_id)
        total_sells = base_sells_query.count()
        total_sells_pages = ceil(total_sells / PER_PAGE)
        offset_sells = (page_sells - 1) * PER_PAGE
        sells = (base_sells_query.offset(offset_sells).limit(PER_PAGE).all())


        base_debts_query = session.query(Debt).filter(Debt.company_id == user.company_id)
        total_debts = base_debts_query.count()
        total_debts_pages = ceil(total_debts / PER_PAGE)
        offset_debts = (page_debts - 1) * PER_PAGE
        pending_debts = (base_debts_query.offset(offset_debts).limit(PER_PAGE).all())

        base_receivables_query = session.query(Receivable).filter(Receivable.company_id == user.company_id)
        total_receivables = base_receivables_query.count()
        total_receivables_pages = ceil(total_receivables / PER_PAGE)
        offset_receivables = (page_receivables - 1) * PER_PAGE
        receivables = (base_receivables_query.offset(offset_receivables).limit(PER_PAGE).all())
        
        kdi_data = kdis_calculate(user, session)
        chart_data = financial_transaction_charts(user, session)
        today = date.today()
        

        return templates.TemplateResponse("financery/financery_dashboard.html", {
            "request": request,
            "sells": sells,
            "kdi_data": kdi_data,
            "chart_data": chart_data,
            "pending_debts": pending_debts,
            "receivables": receivables,
            "today": today,
            "user": user,
            "page_sells": page_sells,
            "page_debts": page_debts,
            "page_receivables": page_receivables,

            "total_sells_pages": total_sells_pages,
            "total_debts_pages": total_debts_pages,
            "total_receivables_pages": total_receivables_pages,
        })
        
    else:
        return ValueError('No Owner')