from fastapi import HTTPException, status
from datetime import datetime

from typing import List

from starlette.responses import JSONResponse

from backend.app.repository.booking import BookingRepository
from backend.app.models.booking import Booking
from backend.app.responses.booking import *
from backend.app.schemas.booking import *

from backend.app.repository.rooms import RoomsRepository


class BookingService:
    def __init__(self, booking_repository: BookingRepository, room_repository: RoomsRepository):
        self.booking_repository = booking_repository
        self.room_repository = room_repository

    async def create_booking(self, data: BookingCreateSchema):

        room_occupancy = self.room_repository.get_room_occupancy_count(data.room_id)

        print(f"Room Occupancy:{room_occupancy}")

        room_capacity = self.room_repository.get_room_capacity_count(data.room_id)
        print(f"Room Capacity: {room_capacity}")

        if room_occupancy >= room_capacity:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Room is already full")

        booking = Booking(
            student_name=data.student_name,
            student_email=data.student_email,
            student_phone=data.student_phone,
            student_course=data.student_course,
            student_study_year=data.student_study_year,
            student_university=data.student_university,

            home_address=data.home_address,
            home_district=data.home_district,
            home_country=data.home_country,

            next_of_kin_name=data.next_of_kin_name,
            next_of_kin_phone=data.next_of_kin_phone,
            kin_relationship=data.kin_relationship,

            hostel_id=data.hostel_id,
            room_id=data.room_id,

            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.booking_repository.create_booking(booking)

        # Increment room occupancy count after successful booking
        self.room_repository.increment_room_occupancy(booking.room_id)

        # TODO: Send Email notification for the booking

        return JSONResponse("Booking received successfully waiting for approval and payment.")

    async def update_booking(self, data: BookingUpdateSchema):
        # Fetch the existing booking from the database
        booking = self.booking_repository.get_booking_by_booking_id(data.booking_id)

        if not booking:
            return JSONResponse(status_code=404, content={"message": "Booking not found"})

        # Update fields if they are provided in the request data
        if data.student_name is not None:
            booking.student_name = data.student_name

        if data.student_email is not None:
            booking.student_email = data.student_email

        if data.student_phone is not None:
            booking.student_phone = data.student_phone

        if data.student_university is not None:
            booking.student_university = data.student_university

        if data.student_course is not None:
            booking.student_course = data.student_course

        if data.student_study_year is not None:
            booking.student_study_year = data.student_study_year

        if data.home_address is not None:
            booking.home_address = data.home_address

        if data.home_district is not None:
            booking.home_district = data.home_district

        if data.home_country is not None:
            booking.home_country = data.home_country

        if data.next_of_kin_name is not None:
            booking.next_of_kin_name = data.next_of_kin_name

        if data.next_of_kin_phone is not None:
            booking.next_of_kin_phone = data.next_of_kin_phone

        if data.kin_relationship is not None:
            booking.kin_relationship = data.kin_relationship

        if data.room_id is not None:
            booking.room_id = data.room_id

        if data.hostel_id is not None:
            booking.hostel_id = data.hostel_id

        # Save the updated booking object to the repository
        self.booking_repository.update_booking(booking)

        # TODO: Send Email notification for the booking update (if needed)

        return JSONResponse(content={"message": "Booking updated successfully"})

    async def cancel_booking(self, booking_id: int):

        booking = self.booking_repository.get_booking_by_booking_id(booking_id)

        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

        if not booking.room_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room for this booking not found.")

        room = self.room_repository.get_room_by_id(booking.room_id)

        room.occupancy -= 1

        self.room_repository.update_room(room)

        # Cancel the booking
        self.booking_repository.delete_booking(booking)

        # TODO: Send email notification to the student

        return JSONResponse("Booking canceled successfully.")

    async def get_booking_by_id(self, booking_id: int) -> BookingResponseSchema:

        booking = self.booking_repository.get_booking_by_booking_id(booking_id)

        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking by user not found")

        booking = BookingResponseSchema(
            id=booking.id,
            student_name=booking.student_name,
            student_email=booking.student_email,
            student_phone=booking.student_phone,
            student_course=booking.student_course,
            student_study_year=booking.student_study_year,
            student_university=booking.student_university,

            home_address=booking.home_address,
            home_district=booking.home_district,
            home_country=booking.home_country,

            next_of_kin_name=booking.next_of_kin_name,
            next_of_kin_phone=booking.next_of_kin_phone,
            kin_relationship=booking.kin_relationship,

            hostel_id=booking.hostel_id,
            room_id=booking.room_id,
            status=booking.status,

            created_at=booking.created_at,
            updated_at=booking.updated_at
        )

        return booking

    async def get_all_my_bookings(self, email: str) -> List[BookingResponseSchema]:
        bookings = self.booking_repository.get_all_my_bookings(email)

        if not bookings:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookings by student email not found")

        bookings = [BookingResponseSchema(
            id=booking.id,
            student_name=booking.student_name,
            student_email=booking.student_email,
            student_phone=booking.student_phone,
            student_course=booking.student_course,
            student_study_year=booking.student_study_year,
            student_university=booking.student_university,

            home_address=booking.home_address,
            home_district=booking.home_district,
            home_country=booking.home_country,

            next_of_kin_name=booking.next_of_kin_name,
            next_of_kin_phone=booking.next_of_kin_phone,
            kin_relationship=booking.kin_relationship,

            hostel_id=booking.hostel_id,
            room_id=booking.room_id,
            status=booking.status,

            created_at=booking.created_at,
            updated_at=booking.updated_at
        ) for booking in bookings]

        return bookings






