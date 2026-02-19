from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from inventory.inventory_model import Inventory
from inventory.inventory_schema import ItemCreate
from users.users_model import User
from core.security import verify_token
from inventory.inventory_service import edit_inventory_item, delete_inventory_item, change_inventory_quantity
from core.dependencies import templates

inventory_router = APIRouter(prefix="/inv", tags=["inv"])
    

@inventory_router.post("/add")
def create_inventory_item(item_name: str = Form(...), description: str = Form(...), quantity: int = Form(...), session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    
    new_item = Inventory(
        item_name=item_name,
        description=description,
        quantity=quantity,
        owner_id=user.id
    )

    session.add(new_item)
    session.commit()
    session.refresh(new_item)

    return RedirectResponse(url="/inv/dashboard", status_code=303)


@inventory_router.post("/add-stock/{inventory_id}")
def add_stock(inventory_id: int, quantity: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    
    change_inventory_quantity(
        inventory_id=inventory_id,
        quantity_delta=quantity,
        action="addition",
        session=session,
        user=user
    )

    session.add(change_inventory_quantity)
    session.commit()
    session.refresh(change_inventory_quantity)

    return RedirectResponse(url="/inv/dashboard", status_code=303)


@inventory_router.post("/edit/{item_name}")
def update_inventory_item(item_name: str, item_update: ItemCreate, session: Session = Depends(CreateSession)):
    edit_inventory_item(item_name, item_update, session)
    return RedirectResponse(url="/inv/dashboard", status_code=303)


@inventory_router.post("/delete/{item_name}")
def delete_inventory_item_route(item_name: str, session: Session = Depends(CreateSession)):
    delete_inventory_item(item_name, session)
    return RedirectResponse(url="/inv/dashboard", status_code=303)


@inventory_router.post("/remove-stock/{inventory_id}")
def remove_stock(
    inventory_id: int,
    quantity: int,
    session: Session = Depends(CreateSession),
    user: User = Depends(verify_token)
):
    change_inventory_quantity(
        inventory_id=inventory_id,
        quantity_delta=-quantity,
        action="removal",
        session=session,
        user=user
    )

    return RedirectResponse(url="/inv/dashboard", status_code=303)



@inventory_router.get("/dashboard")
def inventory_dashboard(request: Request, search: str = None, session: Session = Depends(CreateSession), user: User = Depends(verify_token)
):
    query = session.query(Inventory)

    if search:
        query = query.filter(Inventory.item_name.ilike(f"%{search}%"))

    items = query.all()

    return templates.TemplateResponse(
        "inv/dashboard.html",
        {
            "request": request,
            "items": items,
            "user": user
        }
    )



#proxima tarefa, quero que el inventory_log seja criado automaticamente toda vez que um item for editado ou deletado, e que ele armazene o id do 
#item, o id do usuário que fez a ação, a ação realizada (adição, remoção, edição) e a quantidade alterada (se aplicável) dentro do endpoint de edição e deleção do item. 
#O endpoint de leitura do inventário deve retornar também os logs relacionados a cada item, para que seja possível acompanhar o histórico de alterações de cada item.
#e na leitura do inventário, quero que seja possível filtrar os itens por nome, para facilitar a busca por itens específicos.