from pydantic import BaseModel, Field

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"