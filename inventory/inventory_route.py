from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from inventory.inventory_model import Inventory
from inventory.inventory_schema import ItemCreate, ItemRead

inventory_router = APIRouter(prefix="/inv", tags=["inv"])

@inventory_router.get("/")
def read_inventory(session: Session = Depends(CreateSession)):
    inventory_items = session.query(Inventory).all()

    if not inventory_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No inventory items found")
    
    return inventory_items
    
@inventory_router.post("/add")
def create_inventory_item(item: ItemCreate, session: Session = Depends(CreateSession)):

    new_item = Inventory(
        item_name=item.item_name,
        description=item.description,
        quantity=item.quantity,
        owner_id=item.owner_id
    )

    session.add(new_item)
    session.commit()
    session.refresh(new_item)

    if not new_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create inventory item, check the data provided")

    return {
        "message": "Inventory item created successfully",
        "item": new_item
    }