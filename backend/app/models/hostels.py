from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func, Index, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import event

import enum
from backend.app.database.database import Base

class Hostel(Base):
    """
    Represents a hostel in the system.
    """
    __tablename__ = "hostels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    image_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Links to User
    average_price = Column(Integer, nullable=False)
    available_rooms = Column(Integer, nullable=False, default=0)
    amenities = Column(Text, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Full-text search vector
    search_vector = Column(TSVECTOR, server_default="")

    # Relationships
    owner = relationship("User", back_populates="hostels")  # Links to User.hostels
    rooms = relationship("Room", back_populates="hostel", cascade="all, delete-orphan")

    # Create GIN index for the search_vector column
    __table_args__ = (
        Index("fts_idx", "search_vector", postgresql_using="gin"),
    )

# Register the DDL trigger via event listener
@event.listens_for(Hostel.__table__, 'after_create')
def create_trigger(target, connection, **kwargs):
    connection.execute("""
        CREATE TRIGGER tsvector_update BEFORE INSERT OR UPDATE
        ON hostels FOR EACH ROW EXECUTE FUNCTION
        tsvector_update_trigger(search_vector, 'pg_catalog.english', name, location, description, amenities);
    """)

class RoomType(enum.Enum):
    SINGLE = "single"
    DOUBLE = "double"


class Rooms(Base):
    """
    Represents a room in a hostel
    """

    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=False)
    room_number = Column(String(50), nullable=False, unique=True)
    price_per_semester = Column(Float, nullable=False)
    room_type = Column(Enum(RoomType), nullable=False, default=RoomType.DOUBLE)
    availability = Column(Boolean, default=True)
    capacity = Column(Integer, nullable=False, default=2)
    bathroom = Column(Boolean, nullable=False,default=False)
    balcony = Column(Boolean, nullable=False, default=False)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationship to hostel (a room belongs to a hostel)
    hostel = relationship("Hostel", back_populates="rooms")

