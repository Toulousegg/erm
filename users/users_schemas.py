from pydantic import BaseModel, Field, EmailStr

class UserSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr #validacion de email, si no es un email valido, va a lanzar una excepcion
    password: str = Field(..., min_length=8) #minimo 8 caracteres para la contraseña
    fullname: str = Field(..., min_length=3, max_length=50) #nombre completo no puede estar vacio

    class Config:
        from_attributes = True

class UserLoginSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=50) 
    password: str = Field(..., min_length=8)
    class Config:
        from_attributes = True