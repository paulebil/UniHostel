from pydantic import BaseModel, constr, conint, HttpUrl
from typing import Optional, List
from datetime import datetime

class Images(BaseModel):
    url: HttpUrl


class HostelResponse(BaseModel):
    """
    Pydantic model for serializing hostel data in API responses.
    """
    id: int
    name: constr(min_length=1, max_length=255)
    description: constr(min_length=1)
    location: constr(min_length=1, max_length=255)
    owner_id: conint(ge=1)
    average_price: conint(ge=1)
    available_rooms: conint(ge=0)
    rules_and_regulations: List[str]
    amenities: Optional[str] = None
    image_url: List[Images]
    created_at: datetime  # Use datetime for proper date handling
    updated_at: Optional[datetime] = None  # Use datetime for proper date handling

class HostelListResponse(BaseModel):
    """
    Pydantic model for returning a list of hostels in API responses.
    """
    hostels: List[HostelResponse]

class HostelSearchResponse(BaseModel):
    """
    Pydantic model for returning hostel search results
    """
    results: List[HostelResponse]


