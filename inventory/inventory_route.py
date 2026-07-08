from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import RedirectResponse
from math import ceil
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from inventory.inventory_model import Inventory
from inventory.inventory_schema import ItemCreate
from users.users_model import User
from core.security import verify_token
from inventory.inventory_service import edit_inventory_item, delete_inventory_item, create_inventory_item
from core.dependencies import templates
from utilities.limiter.limiter import limiter
from moduls.dependencies import require_module

inventory_router = APIRouter(prefix="/inv", tags=["inv"])

@inventory_router.post("/add", dependencies=[Depends(require_module("inventory"))])
@limiter.limit("5/minute")
def create_inventory_item_route(request: Request, item_name: str = Form(...), description: str = Form(...), quantity: int = Form(...), session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    create_inventory_item(item_name, description, quantity, session, user)
    return RedirectResponse(url="/inv/dashboard", status_code=303)


@inventory_router.post("/edit/{item_name}", dependencies=[Depends(require_module("inventory"))])
@limiter.limit("5/minute")
def update_inventory_item_route(request: Request, item_name: str, item_name_new: str = Form(...), description: str = Form(...), quantity: int = Form(...), session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    item_update = ItemCreate(item_name=item_name_new, description=description, quantity=quantity, owner_id=user.id)
    edit_inventory_item(item_name, item_update, user, session)
    return RedirectResponse(url="/inv/dashboard", status_code=303)


@inventory_router.post("/delete/{item_name}", dependencies=[Depends(require_module("inventory"))])
@limiter.limit("5/minute")
def delete_inventory_item_route(request: Request, item_name: str, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    delete_inventory_item(item_name, user, session)
    return RedirectResponse(url="/inv/dashboard", status_code=303)


@inventory_router.get("/dashboard", dependencies=[Depends(require_module("inventory"))])
def inventory_dashboard(request: Request, search: str = None, session: Session = Depends(CreateSession), user: User = Depends(verify_token), page_items: int = Query(1, ge=1)):
    PER_PAGE = 30
    
    base_query = session.query(Inventory).filter(Inventory.company_id == user.company_id)
    total_items = base_query.count()
    total_items_page = ceil(total_items / PER_PAGE)
    offset_pages = (page_items - 1) * PER_PAGE
    item_per_page = (base_query.offset(offset_pages).limit(PER_PAGE).all())
    
    
    return templates.TemplateResponse(
        "inv/dashboard.html",
        {
            "request": request,
            "items": [{"item_name": item.item_name,
                        "id": item.id,
                        "description": item.description, 
                        "quantity": item.quantity,
                        "updated_at": item.updated_at,
                        "owner": item.owner.username
                        } 
                        for item in item_per_page
                        ],
            "user": user,
            "page": page_items,
            "total_pages": total_items_page,
            "param": "items_page"
        })


#proxima tarefa, quero que el inventory_log seja criado automaticamente toda vez que um item for editado ou deletado, e que ele armazene o id do 
#item, o id do usuário que fez a ação, a ação realizada (adição, remoção, edição) e a quantidade alterada (se aplicável) dentro do endpoint de edição e deleção do item. 
#O endpoint de leitura do inventário deve retornar também os logs relacionados a cada item, para que seja possível acompanhar o histórico de alterações de cada item.
#e na leitura do inventário, quero que seja possível filtrar os itens por nome, para facilitar a busca por itens específicos.