from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import enum

class RoomType(str,enum.Enum):
    DOUBLE = "DOUBLE"
    SINGLE = "SINGLE"


class RoomCreateSchema(BaseModel):
    hostel_id: int
    room_number: str
    price_per_semester: float
    room_type: RoomType
    capacity: int = 2
    description: str


class RoomUpdateSchema(BaseModel):
    hostel_id: Optional[int] = None
    room_number: Optional[str] = None
    price_per_semester: Optional[float] = None
    room_type: Optional[RoomType] = None
    availability: Optional[bool] = None
    capacity: Optional[int] = None
    bathroom: Optional[bool] = None
    balcony: Optional[bool] = None
    image_url: Optional[str] = None


class DeleteRoomSchema(BaseModel):
    hostel_id: Optional[int] = None
    room_number: Optional[str] = None
