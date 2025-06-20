from sqlalchemy import Boolean, Column, DateTime, Integer, String, func, ForeignKey, Enum
from backend.app.database.database import Base
from sqlalchemy.orm import mapped_column, relationship
import enum

class UserRole(enum.Enum):
    STUDENT = "student"
    HOSTEL_OWNER = "hostel_owner"
    ADMIN = "admin"


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150))
    email = Column(String(255), unique=True, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STUDENT)  # Fixed here
    mobile = Column(Integer, unique=True)
    password = Column(String(100))
    is_active = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True, default=None, onupdate=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), server_onupdate=func.now())

    tokens = relationship("UserToken", back_populates="user", cascade="all, delete")
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete")
    hostels = relationship("Hostel", back_populates="user", cascade="all, delete")

    def get_context_string(self, context: str):
        return f"{context}{self.password[-6:]}{self.mobile}".strip()



class UserToken(Base):
    __tablename__ = 'user_tokens'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(ForeignKey('users.id'))
    access_key = Column(String(250), nullable=True, index=True, default=None)
    refresh_key = Column(String(250), nullable=True, index=True, default=None)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    user = relationship("User", back_populates="tokens")


class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token_hash = Column(String(255), nullable=False)  # Store the hashed token
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)  # Set expiration for token

    user = relationship("User", back_populates="password_reset_tokens")

    def __repr__(self):
        return f"<PasswordResetToken(user_id={self.user_id}, token_hash={self.token_hash})>"