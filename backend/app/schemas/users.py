from pydantic import BaseModel, EmailStr, constr, SecretStr

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

#  This is for the routes
class CreateUser(UserCreateSchema):
    email: EmailStr

class ActivateUser(ActivateUserSchema):
    email: EmailStr

class UserLogin(UserLoginSchema):
    password: SecretStr

class ForgotPassword(UserForgotPasswordSchema):
    email: EmailStr

class RestPassword(UserRestPasswordSchema):
    email: EmailStr
    password: SecretStr