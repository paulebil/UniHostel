from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    mobile: int

class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"

class AllUserResponse(UserResponse):
    role: str
    is_active: bool
    verified_at: Optional[datetime]
    updated_at: datetime