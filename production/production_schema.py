from pydantic import BaseModel, Field
from datetime import date

class production_schema(BaseModel):
    client_name: str = Field(..., max_length=255)
    project_name: str = Field(..., max_length=255)
    delivery_date: date
    description: str = Field(..., max_length=500)

    class Config:
        from_attributes = True

class query_production(BaseModel):
    client_name: str = Field(..., max_length=255)

    class Config:
        from_attributes = True

class create_production(BaseModel):
    client_name: str = Field(..., max_length=255)
    project_name: str = Field(..., max_length=255)
    delivery_date: date
    description: str = Field(..., max_length=500)

    class Config:
        from_attributes = True