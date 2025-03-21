from pydantic import BaseModel,constr, conint
import enum

class UserRole(str, enum.Enum):
    STUDENT = "STUDENT"
    HOSTEL_OWNER = "HOSTEL_OWNER"
    ADMIN = "ADMIN"

class UserCreateSchema(BaseModel):
    name: str
    email: str
    mobile: conint(ge=1000000000, le=999999999999999)  # Ensures 10-15 digits
    role: UserRole
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


