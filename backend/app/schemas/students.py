from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Base schema for Student (Shared fields)
class StudentBase(BaseModel):
    university_name: str
    student_number: str

# Create schema for creating a new student
class StudentCreate(StudentBase):
    email: str
    mobile: int

# Update schema for updating an existing student
class StudentUpdate(StudentBase):
    email: Optional[str]
    mobile: Optional[int]
    name: Optional[str]






