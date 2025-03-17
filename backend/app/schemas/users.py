from pydantic import BaseModel,constr

class UserCreateSchema(BaseModel):
    name: str
    email: str
    password: constr(min_length=8)

class ActivateUserSchema(BaseModel):
    email: str
    token: str

class UserLoginSchema(BaseModel):
    username: str
    password: str

class UserForgotPasswordSchema(BaseModel):
    email: str

class UserRestPasswordSchema(BaseModel):
    email: str
    token: str
    password: constr(min_length=8)


