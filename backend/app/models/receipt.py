from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func

from backend.app.database.database import Base
import enum

class ReceiptStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(Enum(ReceiptStatus), nullable=False, default=ReceiptStatus.PENDING)

    file_name = Column(String(50), nullable=True)
    bucket_name = Column(String(50), nullable=True)
    object_name = Column(String(50), nullable=True)
    version_id = Column(String(50), nullable=True)
    etag = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())