from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from inventory.inventory_model import Inventory
from inventory.inventory_schema import ItemCreate
from users.users_model import User
from core.security import verify_token, create_token
from inventory.inventory_service import edit_inventory_item, delete_inventory_item

inventory_router = APIRouter(prefix="/inv", tags=["inv"])

@inventory_router.get("/")
def read_inventory(session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    access_token = create_token(user.id)

    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized, invalid token")

    inventory_items = session.query(Inventory).all()

    if not inventory_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No inventory items found")
    
    return {
        "message": "Inventory items retrieved successfully",
        "items": inventory_items
    }
    
@inventory_router.post("/add")
def create_inventory_item(itemcreate: ItemCreate, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    access_token = create_token(user.id)

    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized, invalid token")
    
    new_item = Inventory(
        item_name=itemcreate.item_name,
        description=itemcreate.description,
        quantity=itemcreate.quantity,
        owner_id=itemcreate.owner_id
    )

    if new_item.owner_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner ID is required to create an inventory item")
    
    converter_id_to_username = session.query(User.username).filter(User.id == new_item.owner_id).first()

    if not converter_id_to_username:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Owner not found, please provide a valid owner ID")
    
    if new_item.item_name in [item.item_name for item in session.query(Inventory.item_name).all()]:
        session.add(new_item)
        session.commit()
        session.refresh(new_item)

    session.add(new_item)
    session.commit()
    session.refresh(new_item)

    if not new_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create inventory item, check the data provided")

    return {
        "message": "Inventory item created successfully",
        "item": new_item,
    }

@inventory_router.put("/edit/{item_name}")
def update_inventory_item(item_name: str, item_update: ItemCreate, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    return edit_inventory_item(item_name, item_update, session, user)

@inventory_router.delete("/delete/{item_name}")
def delete_inventory_item_route(item_name: str, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    return delete_inventory_item(item_name, session, user)


#proxima tarefa, quero que el inventory_log seja criado automaticamente toda vez que um item for editado ou deletado, e que ele armazene o id do 
#item, o id do usuário que fez a ação, a ação realizada (adição, remoção, edição) e a quantidade alterada (se aplicável) dentro do endpoint de edição e deleção do item. 
#O endpoint de leitura do inventário deve retornar também os logs relacionados a cada item, para que seja possível acompanhar o histórico de alterações de cada item.
#e na leitura do inventário, quero que seja possível filtrar os itens por nome, para facilitar a busca por itens específicos.