from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Boolean, DateTime, func, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


from backend.app.database.database import Base


class ImageType(enum.Enum):
    HOSTEL = "hostel"
    ROOM = "room"

class Image(Base):

    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    url = Column(String(255), nullable=True)
    image_type = Column(Enum(ImageType), nullable=False)
    hostel_id = Column(Integer, ForeignKey("hostels.id"), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    is_primary = Column(Boolean, default=False)

    file_name = Column(String(50), nullable=True)
    bucket_name = Column(String(50), nullable=True)
    object_name = Column(String(50), nullable=True)
    version_id = Column(String(50), nullable=True)
    etag = Column(String(50), nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    hostel = relationship("Hostel", backref="images", foreign_keys=[hostel_id])
    room = relationship("Room", backref="images", foreign_keys=[room_id])

    def __repr__(self):
        return f"<Image(url={self.url}, image_type={self.image_type}, is_primary={self.is_primary})>"

    @classmethod
    def mark_primary(cls, session, image_id: int):
        # Mark a single image as primary
        image = session.query(cls).filter(cls.id == image_id).first()
        if image:
            # Mark the image as primary
            image.is_primary = True
            session.commit()
            return image
        return None

    @classmethod
    def unmark_primary(cls, session, hostel_id: int = None, room_id: int = None):
        # Unmark the primary image for a hostel or room (optional if the hostel room is provided)
        query = session.query(cls).filter(cls.is_primary == True)
        if hostel_id:
            query = query.filter(cls.hostel_id == hostel_id)
        if room_id:
            query = query.filter(cls.room_id == room_id)

        primary_image = query.first()
        if primary_image:
            primary_image.is_primary = False
            session.commit()
            return primary_image
        return None

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