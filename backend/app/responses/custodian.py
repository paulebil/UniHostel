from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Base schema for HostelOwner (Shared fields)
class HostelOwnerBase(BaseModel):
    business_name: str

# Response schema for HostelOwner
class HostelOwnerResponse(HostelOwnerBase):
    id: int
    email: EmailStr
    mobile: int
    name: str
    is_active: bool
    verified_at: Optional[datetime]
    updated_at: datetime
