from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, DateTime, func,
    Index, Computed, Float,Enum
)
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
    rules_and_regulations = Column(Text, nullable=True)
    amenities = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Full-text search vector (auto-updating)
    search_vector = Column(
        TSVECTOR,
        Computed("to_tsvector('english', name || ' ' || location || ' ' || description || COALESCE(amenities, ''))",
                 persisted=True)
    )

    # Relationships
    owner = relationship("User", back_populates="hostels")
    rooms = relationship("Room", back_populates="hostel", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="hostel", cascade="all, delete-orphan")

    # Create GIN index for the search_vector column
    __table_args__ = (
        Index("fts_idx", "search_vector", postgresql_using="gin"),
    )

    def get_rules(self):
        if self.rules_and_regulations:
            # Split the string by commas, strip each rule of excess spaces,
            # and convert each rule to sentence case.
            return [rule.strip().capitalize() for rule in self.rules_and_regulations.split(',')]
        return []


# # Register the DDL trigger via event listener
# @event.listens_for(Hostel.__table__, 'after_create')
# def create_trigger(target, connection, **kwargs):
#     connection.execute("""
#         CREATE TRIGGER tsvector_update BEFORE INSERT OR UPDATE
#         ON hostels FOR EACH ROW EXECUTE FUNCTION
#         tsvector_update_trigger(search_vector, 'pg_catalog.english', name, location, description, amenities);
#     """)

class RoomType(enum.Enum):
    SINGLE = "single"
    DOUBLE = "double"


class Room(Base):
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
    occupancy = Column(Integer, nullable=True, default=0)
    bathroom = Column(Boolean, nullable=False,default=False)
    balcony = Column(Boolean, nullable=False, default=False)
    image_url = Column(String(255), nullable=True)
    booked_status = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Relationship to hostel (a room belongs to a hostel)
    hostel = relationship("Hostel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room", cascade="all, delete-orphan")





