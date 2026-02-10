from pydantic import BaseModel


class InventoryBase(BaseModel):
    name: str
    quantity: int
    description: str

    class config:
        from_attributes = True

class ItemCreate(InventoryBase):
    name: str  
    quantity: int
    description: str
    owner_id: int

    class Config:
        from_attributes = True

class ItemRead(InventoryBase):
    id: int

    class Config:
        from_attributes = True