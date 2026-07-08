from fastapi import APIRouter, Depends, Request, Form, HTTPException, status, Query
from math import ceil
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates
from core.security import verify_token
from contacts.contacts_models import Contacts
from contacts.contacts_services import CreateContact, update_contact, delete_contact
from contacts.contacts_schema import ContactsBase, ContactUpdate
from users.users_model import User
from utilities.limiter.limiter import limiter
from moduls.dependencies import require_module


contacts_router = APIRouter(prefix="/ctc", tags=["ctc"])

@contacts_router.post("/add", dependencies=[Depends(require_module("ctc"))])
@limiter.limit("5/minute")
def create_contact(request: Request, name: str = Form(...), email: str | None = Form(None), phone: str = Form(...), type: str = Form(...), user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    
    contact = ContactsBase(
        name=name,
        email=email,
        phone=phone,
        type=type
    )  

    CreateContact(contact, user, session)
    
    return RedirectResponse(url="/ctc", status_code=303)

@contacts_router.put("/edit/{contactId}", dependencies=[Depends(require_module("ctc"))])
@limiter.limit("7/minute")
def edit_contact(request: Request, contactId: int, data: ContactUpdate, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    return update_contact(session, contactId, user, data.name, data.email, data.phone, data.type)

@contacts_router.delete("/delete/{contactId}", dependencies=[Depends(require_module("ctc"))])
@limiter.limit("7/minute")
def delete_contact_router(request: Request, contactId: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    return delete_contact(session, contactId, user)

#VIEWS

@contacts_router.get("/", dependencies=[Depends(require_module("ctc"))])
def get_contacts(request: Request, session: Session = Depends(CreateSession), user: User = Depends(verify_token), page_contacts: int = Query(1, ge=1)):
    PER_PAGE = 30
    
    base_query =  session.query(Contacts).filter(Contacts.company_id == user.company_id)
    total_contacts = base_query.count()
    total_contacts_page = ceil(total_contacts / PER_PAGE)
    offset_pages = (page_contacts - 1) * PER_PAGE
    contacts_per_page = (base_query.offset(offset_pages).limit(PER_PAGE).all())

    return templates.TemplateResponse(
        "contacts/contacts.html",
        {
            "request": request,
            "user": user,
            "page": page_contacts,
            "total_pages": total_contacts_page,
            "param": "page_contacts",
            "items": [{"name": contact.name,
                        "id": contact.id,
                        "phone": contact.phone, 
                        "type": contact.type,
                        "email": contact.email,
                        } 
                        for contact in contacts_per_page
                        ],
            
        }
    )