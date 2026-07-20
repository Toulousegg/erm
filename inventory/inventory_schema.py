from pydantic import BaseModel, Field
from datetime import date
from enum import Enum

class action(str, Enum):
    Delete = "Delete"
    Reduce = "Reduce"
    Add = "Add"

class InventoryBase(BaseModel):
    item_name: str
    quantity: int
    description: str = Field(..., max_length=255) #descripcion no puede ser mayor a 255 caracteres

    class Config:
        from_attributes = True

class ItemCreate(InventoryBase):
    owner_id: int

    class Config:
        from_attributes = True

class ItemRead(BaseModel):
    id: int

    class Config:
        from_attributes = True

class InvLog(BaseModel):
    inventory_id: int
    user_id: int
    action: action
    timestamp: date

    class Config:
        from_attributes = True

class OutputItem(BaseModel):
    code: str
    quantity: int

class InventoryOutputRequest(BaseModel):
    worker_id: int
    items: list[OutputItem]