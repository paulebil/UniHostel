from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Base schema for Student (Shared fields)
class StudentBase(BaseModel):
    university_name: str
    student_number: str


# Response schema for Student
class StudentResponse(StudentBase):
    id: int
    email: EmailStr
    mobile: int
    name: str
    is_active: bool
    verified_at: Optional[datetime]
    updated_at: datetime