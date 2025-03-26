from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RoomResponse(BaseModel):
    id: int
    hostel_id: int
    room_number: str
    price_per_semester: float
    room_type: str
    availability: bool
    capacity: int
    bathroom: bool
    balcony: bool
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

