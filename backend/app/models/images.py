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

    draft_id = Column(String(36), nullable=True, index=True)

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


class PDFDocumentMetadata(Base):
    __tablename__ = 'pdf_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String, nullable=False)
    minio_url = Column(String, nullable=False)
    content_type = Column(String, nullable=False)  # e.g., 'application/pdf'
    bucket_name = Column(String(50), nullable=True)
    object_name = Column(String(50), nullable=True)
    version_id = Column(String(50), nullable=True)
    etag = Column(String(50), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return f"<PDFDocumentMetadata(id={self.id}, file_name={self.file_name}, uploaded_at={self.uploaded_at})>"