from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from inventory.inventory_model import Inventory
from inventory.inventory_schema import ItemCreate, ItemRead
from users.users_model import User

inventory_router = APIRouter(prefix="/inv", tags=["inv"])

@inventory_router.get("/")
def read_inventory(session: Session = Depends(CreateSession)):
    inventory_items = session.query(Inventory).all()

    if not inventory_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No inventory items found")
    
    return {
        "message": "Inventory items retrieved successfully",
        "items": inventory_items
    }
    
@inventory_router.post("/add")
def create_inventory_item(itemcreate: ItemCreate, session: Session = Depends(CreateSession)):

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

    session.add(new_item)
    session.commit()
    session.refresh(new_item)

    if not new_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create inventory item, check the data provided")

    return {
        "message": "Inventory item created successfully",
        "item": new_item,
    }