from pydantic import BaseModel, EmailStr, constr

class UserCreateSchema(BaseModel):
    name: str
    email: EmailStr
    password: constr(max_length=8)

class UserActivateSchema(BaseModel):
    email: EmailStr
    token: str

class UserLoginSchema(BaseModel):
    username: str
    password: str

class UserForgotPasswordSchema(BaseModel):
    email: EmailStr

class UserRestPasswordSchema(BaseModel):
    email: EmailStr
    token: str
    password: constr(min_length=8)