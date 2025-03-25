from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    func,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy import event
from backend.app.database.database import Base

class Hostel(Base):
    """
    Represents a hostel in the system.
    """
    __tablename__ = "hostels"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Links to User
    price_per_month = Column(Integer, nullable=False)
    available_rooms = Column(Integer, nullable=False, default=0)
    amenities = Column(Text, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    # Full-text search vector
    search_vector = Column(TSVECTOR, server_default="")

    # Relationships
    owner = relationship("User", back_populates="hostels")  # Links to User.hostels

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
