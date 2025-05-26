from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List

class Images(BaseModel):
    url: HttpUrl


class RoomResponse(BaseModel):
    id: int
    hostel_id: int
    room_number: str
    price_per_semester: float
    room_type: str
    availability: bool
    image_url: List[Images]
    created_at: datetime
    updated_at: datetime

class AllRoomsResponse(BaseModel):
    rooms: List[RoomResponse]
