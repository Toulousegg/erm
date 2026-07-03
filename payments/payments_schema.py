from pydantic import AliasChoices, BaseModel, Field

class SubscriptionCreate(BaseModel):
    module_ids: list[int] = Field(validation_alias=AliasChoices("module_ids", "modules"))
    
    class Config:
        from_attributes = True
