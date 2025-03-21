from sqlalchemy.orm import Session
from backend.app.models.users import User,Student
from sqlalchemy.exc import IntegrityError


class StudentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_student(self, student: Student) -> None:
        try:
            self.session.add(student)
            self.session.commit()
            self.session.refresh(student)
        except IntegrityError:
            self.session.rollback()
            raise

    def update_student(self, student: Student) -> None:
        try:
            self.session.commit()
            self.session.refresh(student)
        except IntegrityError:
            self.session.rollback()
            raise

    def delete_student(self, student: Student) -> None:
        self.session.delete(student)
        self.session.commit()

    def get_student_by_user_id(self, user_id: int) -> Student:
        student = self.session.query(Student).filter(Student.user_id == user_id).first()
        return student

    def get_student_by_user_email(self, email: str) -> Student:
        return self.session.query(Student).join(User).filter(User.email == email).first()

    def get_student_by_user_mobile(self, mobile: int) -> Student:
        return self.session.query(Student).join(User).filter(User.mobile == mobile).first()

