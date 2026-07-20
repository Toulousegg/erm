from fastapi import HTTPException, status, WebSocket
from sqlalchemy.orm import Session
from inventory.inventory_model import Inventory, InventoryLog
from inventory.inventory_schema import ItemCreate
from users.users_model import User
from core.barcode_service import generate_barcode_image, generate_code128

def _create_inventory_log(session: Session, inventory_id: int, user_id: int, action: str, quantity_changed: int = None, details: str = None):
    log_entry = InventoryLog(
        inventory_id=inventory_id,
        user_id=user_id,
        action=action,
        quantity_changed=quantity_changed,
        details=details,
    )
    session.add(log_entry)
    return log_entry


def create_inventory_item(item_name: str, description: str, quantity: int, session: Session, user: User):
    
    new_item = Inventory(
        item_name=item_name,
        description=description,
        quantity=quantity,
        owner_id=user.id,
        company_id=user.company_id
    )

    session.add(new_item)
    session.flush()
    
    code = generate_code128(new_item.id)
    
    new_item.code = f"PRD-{code}"

    _create_inventory_log(
        session,
        inventory_id=new_item.id,
        user_id=user.id,
        action='addition',
        quantity_changed=quantity,
        details='Inventory item created'
    )
    session.commit()
    session.refresh(new_item)

    return {
        "message": "Inventory item created successfully",
        "item": new_item.item_name,
        "code": new_item.code
    }

def edit_inventory_item(item_name: str, item_update: ItemCreate, user: User, session: Session):

    if not user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User not authenticated")
    
    item = session.query(Inventory).filter(Inventory.item_name == item_name, Inventory.company_id == user.company_id).first()

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    previous_quantity = item.quantity
    item.item_name = item_update.item_name
    item.description = item_update.description
    item.quantity = item_update.quantity
    item.owner_id = user.id

    session.flush()
    _create_inventory_log(
        session,
        inventory_id=item.id,
        user_id=user.id,
        action='edition',
        quantity_changed=item.quantity - previous_quantity,
        details='Inventory item updated'
    )
    session.commit()
    session.refresh(item)

    return {
        "message": "Inventory item updated successfully",
        "item": item,
    }

def delete_inventory_item(item_name: str, user: User, session: Session): 
    
    if not user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="User not authenticated")

    item_to_delete = session.query(Inventory).filter(Inventory.item_name == item_name, Inventory.company_id == user.company_id).first()

    if not item_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory item not found")

    session.flush()
    _create_inventory_log(
        session,
        inventory_id=item_to_delete.id,
        user_id=user.id,
        action='removal',
        quantity_changed=item_to_delete.quantity,
        details='Inventory item deleted'
    )
    session.delete(item_to_delete)
    session.commit()

    return {
        "message": "Inventory item deleted successfully",
        "item": item_to_delete
    }
    
#____________________________________________________________
#a partir de aqui es puro barcode
#a partir de aqui es puro barcode
#a partir de aqui es puro barcode
#a partir de aqui es puro barcode
#a partir de aqui es puro barcode
#____________________________________________________________

def create_inventory_output(items, worker_id, user, session):
    for item_data in items:

        item = session.query(Inventory).filter(Inventory.code == item_data["code"], Inventory.company_id == user.company_id).first()
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item_data['code']} not found"
            )

        if item.quantity < item_data["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {item.item_name}"
            )

        # descontar stock
        item.quantity -= item_data["quantity"]

        print('4')
        _create_inventory_log(
            session,
            inventory_id=item.id,
            user_id=user.id,
            action="output",
            quantity_changed=-item_data["quantity"],
            details="Barcode inventory output"
        )

    session.commit()

    return {
        "success": True,
        "message": "Inventory output completed"
    }