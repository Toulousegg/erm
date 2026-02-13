from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from inventory.inventory_model import Inventory
from inventory.inventory_schema import ItemCreate
from users.users_model import User
from core.security import verify_token, create_token

def edit_inventory_item(item_name: str, item_update: ItemCreate, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    access_token = create_token(user.id)

    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized, invalid token")
    
    item = session.query(Inventory).filter(Inventory.item_name == item_name).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    item.item_name = item_update.item_name
    item.description = item_update.description
    item.quantity = item_update.quantity
    item.owner_id = item_update.owner_id

    session.commit()
    session.refresh(item)

    return {
        "message": "Inventory item updated successfully",
        "item": item,
    }

def delete_inventory_item(item_name: str, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    access_token = create_token(user.id)

    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized, invalid token")
    
    item_to_delete = session.query(Inventory).filter(Inventory.item_name == item_name).first()

    if not item_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    session.delete(item_to_delete)
    session.commit()

    return {
        "message": "Inventory item deleted successfully",
        "item": item_to_delete
    }