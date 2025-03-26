from pydantic import BaseModel, constr, conint
from typing import Optional

class HostelCreateSchema(BaseModel):
    """
    Pydantic model for creating a new hostel.
    """
    name: constr(min_length=1, max_length=255)
    image_url: Optional[constr(max_length=255)] = None
    description: constr(min_length=1)
    location: constr(min_length=1, max_length=255)
    average_price: conint(ge=1)
    available_rooms: conint(ge=0) = 0
    amenities: Optional[str] = None  # Change to str for consistency with Text field in DB

class HostelUpdateSchema(HostelCreateSchema):
    """
    Pydantic model for updating a hostel
    """
