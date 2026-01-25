from pydantic import BaseModel

class UserSchema(BaseModel):
    username: str
    email: str
    password: str
    fullname: str

    class Config:
        from_attributes = True

class UserLoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True