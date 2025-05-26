from fastapi import HTTPException, status

from typing import List

from starlette.responses import JSONResponse

from backend.app.repository.booking import BookingRepository
from backend.app.models.booking import Booking
from backend.app.responses.booking import *
from backend.app.schemas.booking import *

from backend.app.repository.rooms import RoomsRepository
from backend.app.repository.hostels import HostelRepository
from backend.app.models.users import User


class BookingService:
    def __init__(self, booking_repository: BookingRepository, room_repository: RoomsRepository,
                  hostel_repository: HostelRepository):
        self.booking_repository = booking_repository
        self.room_repository = room_repository
        self.hostel_repository = hostel_repository

    async def create_booking(self, data: BookingCreateSchema):

        if not data.room_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Room id can not be null")
        if not data.hostel_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Hostel id can not be null")

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


    async def get_all_room_booking_by_hostel(self, hostel_id: int, current_user: User) -> List[BookingResponseSchema]:
        # Ensure user is a hostel owner
        owner = self.hostel_owner_repository.get_hostel_owner_by_user_id(current_user.id)
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not registered as a hostel owner."
            )

        # Fetch owned hostels
        owned_hostels = self.hostel_repository.get_all_hostels_by_one_owner(owner.id)
        if not owned_hostels:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not own any hostels."
            )

        # Verify the requested hostel_id belongs to the owner
        hostel_ids = {hostel.id for hostel in owned_hostels}
        if hostel_id not in hostel_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this hostel's bookings."
            )

        # Fetch room bookings
        bookings = self.booking_repository.get_all_room_booking_by_hostel_id(hostel_id)
        if not bookings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No bookings found for this hostel."
            )

        # Convert to response schema
        return [
            BookingResponseSchema(
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
            for booking in bookings
        ]

    async def get_one_room_booking_for_hostel(self, hostel_id: int, booking_id: int, current_user: User) -> BookingResponseSchema:
        # Ensure user is a hostel owner
        owner = self.hostel_owner_repository.get_hostel_owner_by_user_id(current_user.id)
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not registered as a hostel owner."
            )

        # Fetch owned hostels
        owned_hostels = self.hostel_repository.get_all_hostels_by_one_owner(owner.id)
        if not owned_hostels:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not own any hostels."
            )

        # Verify the requested hostel_id belongs to the owner
        hostel_ids = {hostel.id for hostel in owned_hostels}
        if hostel_id not in hostel_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this hostel's bookings."
            )

        # Fetch room booking
        booking = self.booking_repository.get_booking_by_booking_id(booking_id)

        if not booking or booking.hostel_id != hostel_id:  # Ensure the booking belongs to the specified hostel
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No booking found for this hostel."
            )

        # Convert to response schema
        return BookingResponseSchema(
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

