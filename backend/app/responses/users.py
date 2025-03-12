from pydantic import BaseModel, Field

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
