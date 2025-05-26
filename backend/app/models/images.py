from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, func, CheckConstraint
)
from datetime import datetime
from sqlalchemy.orm import relationship
from backend.app.database.database import Base  # your Base import

class ImageMetaData(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    file_name = Column(String(50), nullable=True)
    bucket_name = Column(String(50), nullable=True)
    object_name = Column(String(255), nullable=True)
    version_id = Column(String(50), nullable=True)
    etag = Column(String(50), nullable=True)

    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Enforce either hostel_id or room_id must be set (but not both)
    __table_args__ = (
        CheckConstraint(
            "(hostel_id IS NOT NULL AND room_id IS NULL) OR (hostel_id IS NULL AND room_id IS NOT NULL)",
            name="chk_image_hostel_or_room"
        ),
    )

    # Relationships
    hostel = relationship("Hostel", backref="images", foreign_keys=[hostel_id])
    room = relationship("Room", backref="images", foreign_keys=[room_id])

    def __repr__(self):
        return f"<Image(id={self.id}, url={self.url}, hostel_id={self.hostel_id}, room_id={self.room_id})>"