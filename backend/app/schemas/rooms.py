from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import enum

class RoomType(str,enum.Enum):
    SINGLE = "SINGLE"
    DOUBLE = "DOUBLE"


class RoomCreateSchema(BaseModel):
    hostel_id: int
    room_number: str
    price_per_semester: float
    room_type: RoomType
    availability: bool = True
    capacity: int = 2
    bathroom: bool = False
    balcony: bool = False
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

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
    updated_at: datetime = Field(default_factory=datetime.now)
