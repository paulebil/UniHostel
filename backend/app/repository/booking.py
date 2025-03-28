from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.models.booking import Booking


class BookingRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_booking(self, booking: Booking):
        try:
            self.session.add(booking)
            self.session.commit()
            self.session.refresh(booking)
        except IntegrityError:
            self.session.rollback()
            raise

    def update_booking(self, booking: Booking):
        try:
            self.session.merge(booking)
            self.session.commit()
            self.session.refresh(booking)
        except IntegrityError:
            self.session.rollback()
            raise

    def delete_booking(self, booking: Booking):
        self.session.delete(booking)
        self.session.commit()

    def get_booking_by_booking_id(self, booking_id: int):
        return self.session.query(Booking).filter(Booking.id == booking_id).first()

    def get_all_my_bookings(self, student_email: str):
        return self.session.query(Booking).filter(Booking.student_email == student_email).first()

    def get_all_hostel_room_booking(self):
        return self.session.query(Booking).all()
