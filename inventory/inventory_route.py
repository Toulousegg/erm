from fastapi import APIRouter, Depends, Request, Form, Query
from fastapi.responses import RedirectResponse, StreamingResponse
from math import ceil
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from inventory.inventory_model import Inventory
from inventory.inventory_schema import ItemCreate, InventoryOutputRequest
from users.users_model import User
from core.security import verify_token
from inventory.inventory_service import edit_inventory_item, create_inventory_item, create_inventory_output
from core.dependencies import templates
from utilities.limiter.limiter import limiter
from moduls.dependencies import require_module
from core.dependencies import render_template
from core.barcode_service import generate_barcode_image

inventory_router = APIRouter(prefix="/inv", tags=["inv"])

@inventory_router.post("/add",dependencies=[Depends(require_module("inventory"))])
@limiter.limit("5/minute")
def create_inventory_item_route(request: Request, item_name: str = Form(...), description: str = Form(...), quantity: int = Form(...), session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    item = create_inventory_item(item_name, description, quantity, session, user)

    image = generate_barcode_image(item["code"])

    return StreamingResponse(
        image,
        media_type="image/png",
        headers={
            "Content-Disposition": f"inline; filename={item['code']}.png"
        }
    )

@inventory_router.post("/barcode/output", dependencies=[Depends(require_module("inventory"))])
def barcode_output(data: InventoryOutputRequest, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    return create_inventory_output(
        items=[
            item.model_dump()
            for item in data.items
        ],
        worker_id=data.worker_id,
        user=user,
        session=session
    )

@inventory_router.post("/edit/{item_name}", dependencies=[Depends(require_module("inventory"))])
@limiter.limit("5/minute")
def update_inventory_item_route(request: Request, item_name: str, item_name_new: str = Form(...), description: str = Form(...), quantity: int = Form(...), session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    item_update = ItemCreate(item_name=item_name_new, description=description, quantity=quantity, owner_id=user.id)
    edit_inventory_item(item_name, item_update, user, session)
    return RedirectResponse(url="/inv/dashboard", status_code=303)


@inventory_router.get("/barcode/worker/{code}", dependencies=[Depends(require_module("inventory"))])
def get_worker_by_barcode(code: str, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    worker = session.query(User).filter(User.company_id == user.company_id, User.barcode == code).first()

    if not worker:
        return {
            "success": False,
            "message": "Código inválido"
        }

    return {
    "success": True,
    "worker": {
        "id": worker.id,
        "name": worker.fullname,
        "role": worker.role,
        "can_move_inventory": True
        }
    }

@inventory_router.get("/dashboard", dependencies=[Depends(require_module("inventory"))])
def inventory_dashboard(request: Request, search: str = None, session: Session = Depends(CreateSession), user: User = Depends(verify_token), page_items: int = Query(1, ge=1)):
    PER_PAGE = 30
    
    base_query = session.query(Inventory).filter(Inventory.company_id == user.company_id)

    if search:
        search_value = f"%{search.strip()}%"
        base_query = base_query.filter(Inventory.item_name.ilike(search_value))

    total_items = base_query.count()
    total_items_page = ceil(total_items / PER_PAGE)
    offset_pages = (page_items - 1) * PER_PAGE
    item_per_page = (base_query.offset(offset_pages).limit(PER_PAGE).all())
    
    
    return render_template(
        "inv/dashboard.html", request, session, user,
        {
            "items": [{"item_name": item.item_name,
                        "id": item.id,
                        "description": item.description, 
                        "quantity": item.quantity,
                        "updated_at": item.updated_at,
                        "owner": item.owner.username,
                        "logs": [{
                            "id": log.id,
                            "action": log.action,
                            "quantity_changed": log.quantity_changed,
                            "details": log.details,
                            "created_at": log.created_at,
                            "user_id": log.user_id,
                            "user_name": log.user.username if log.user else None,
                        } for log in item.logs]
                        } 
                        for item in item_per_page
                        ],
            "user": user,
            "page": page_items,
            "total_pages": total_items_page,
            "param": "items_page"
        })
    
@inventory_router.get("/barcode/output", dependencies=[Depends(require_module("inventory"))])
def barcode_output_route(request: Request, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    return render_template(
        "inv/barcode_output.html",
        request=request,
        session=session,
        user=user
    )


#proxima tarefa, quero que el inventory_log seja criado automaticamente toda vez que um item for editado ou deletado, e que ele armazene o id do 
#item, o id do usuário que fez a ação, a ação realizada (adição, remoção, edição) e a quantidade alterada (se aplicável) dentro do endpoint de edição e deleção do item. 
#O endpoint de leitura do inventário deve retornar também os logs relacionados a cada item, para que seja possível acompanhar o histórico de alterações de cada item.
#e na leitura do inventário, quero que seja possível filtrar os itens por nome, para facilitar a busca por itens específicos.