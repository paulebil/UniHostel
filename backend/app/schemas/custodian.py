from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Base schema for HostelOwner (Shared fields)
class HostelOwnerBase(BaseModel):
    business_name: str

# Create schema for creating a new hostel owner
class HostelOwnerCreate(HostelOwnerBase):
    email: str
    mobile: int

# Update schema for updating an existing hostel owner
class HostelOwnerUpdate(HostelOwnerBase):
    email: Optional[str]
    mobile: Optional[int]


