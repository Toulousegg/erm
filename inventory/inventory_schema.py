from pydantic import BaseModel, Field


class InventoryBase(BaseModel):
    item_name: str
    quantity: int
    description: str = Field(..., max_length=50) #descripcion no puede ser mayor a 255 caracteres

    class Config:
        from_attributes = True

class ItemCreate(InventoryBase):
    owner_id: int

    class Config:
        from_attributes = True

class ItemRead(InventoryBase):
    id: int

    class Config:
        from_attributes = True