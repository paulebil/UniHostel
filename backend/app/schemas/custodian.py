from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Base schema for HostelOwner (Shared fields)
class HostelOwnerBase(BaseModel):
    business_name: str

# Create schema for creating a new hostel owner
class HostelOwnerCreate(HostelOwnerBase):
    email: EmailStr
    mobile: int
    name: str
    password: str

# Update schema for updating an existing hostel owner
class HostelOwnerUpdate(HostelOwnerBase):
    email: Optional[EmailStr]
    mobile: Optional[int]
    name: Optional[str]
    password: Optional[str]

