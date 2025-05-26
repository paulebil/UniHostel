from backend.app.models.users import Student
from backend.app.repository.student import StudentRepository
from backend.app.repository.users import UserRepository
from backend.app.schemas.students import *
from backend.app.responses.students import *

from fastapi import HTTPException


class StudentService:
    def __init__(self, student_repository: StudentRepository, user_repository: UserRepository):
        self.student_repository = student_repository
        self.user_repository = user_repository

    async def create_student(self, data: StudentCreate) -> StudentResponse:
        # Check if a student with this email or mobile already exists
        student_exists = self.student_repository.get_student_by_user_email(data.email)
        if student_exists:
            raise HTTPException(status_code=400, detail="Email already exists.")
        student_mobile = self.student_repository.get_student_by_user_mobile(data.mobile)
        if student_mobile:
            raise HTTPException(status_code=400, detail="Mobile number already exists.")

        # Retrieve corresponding user
        corresponding_user = self.user_repository.get_user_by_email(data.email)
        if not corresponding_user:
            raise HTTPException(status_code=404, detail="User not found.")

        # Create Student with user_id
        student = Student(
            user_id=corresponding_user.id,  # ✅ Assign user_id here
            university_name=data.university_name,
            student_number=data.student_number
        )

        self.student_repository.create_student(student)

        # Return student response
        student_response = StudentResponse(
            id=corresponding_user.id,
            email=corresponding_user.email,
            mobile=corresponding_user.mobile,
            name=corresponding_user.name,
            student_number=student.student_number,
            university_name=student.university_name,
            is_active=corresponding_user.is_active,
            verified_at=corresponding_user.verified_at,
            updated_at=corresponding_user.updated_at
        )

        return student_response


    async def update_student(self, data: StudentUpdate) -> StudentResponse:
        # Retrieve the user
        user = self.user_repository.get_user_by_email(data.email)
        if not user:
            raise HTTPException(status_code=400, detail="User with this email does not exist.")

        # Retrieve the student linked to the user
        student = self.student_repository.get_student_by_user_id(user.id)
        if not student:
            raise HTTPException(status_code=404, detail="Student record not found.")

        # Ensure the provided mobile number matches the user
        if user.mobile != data.mobile:
            raise HTTPException(status_code=400, detail="Mobile number does not match the user record.")

        # Update student details
        student.university_name = data.university_name
        student.student_number = data.student_number

        # Save the updated student record
        self.student_repository.update_student(student)

        # Refresh user details after update
        user = self.user_repository.get_user_by_email(data.email)

        # Return updated response
        return StudentResponse(
            id=user.id,
            email=user.email,
            mobile=user.mobile,
            name=user.name,
            student_number=student.student_number,
            university_name=student.university_name,
            is_active=user.is_active,
            verified_at=user.verified_at,
            updated_at=user.updated_at
        )

    async def delete_student(self, email: str):
        # Retrieve the user by email
        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=400, detail="Student information with this email not found.")
        # Retrieve the student record linked to this user
        student = self.student_repository.get_student_by_user_id(user.id)
        if not student:
            raise HTTPException(status_code=400, detail="Student information with this email not found.")

        # Delete the student record
        self.student_repository.delete_student(student)

        return {"message": "Student record deleted successfully."}

    async def get_student_information(self, email: str) -> StudentResponse:
        user_info = self.user_repository.get_user_by_email(email)
        if not user_info:
            raise HTTPException(status_code=400, detail="User Info with this email not found.")

        student_info = self.student_repository.get_student_by_user_email(email)
        if not student_info:
            raise HTTPException(status_code=400, detail="Student Info with this email not found.")

        student_response = StudentResponse(
            id=user_info.id,
            email=user_info.email,
            mobile=user_info.mobile,
            name=user_info.name,
            student_number=student_info.student_number,
            university_name=student_info.university_name,
            is_active=user_info.is_active,
            verified_at=user_info.verified_at,
            updated_at=user_info.updated_at
        )

        return student_response