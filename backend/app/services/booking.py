from fastapi import HTTPException, status

from typing import List

from starlette.responses import JSONResponse

from backend.app.repository.booking import BookingRepository
from backend.app.models.booking import Booking
from backend.app.responses.booking import *
from backend.app.schemas.booking import *

from backend.app.repository.rooms import RoomsRepository
from backend.app.repository.hostels import HostelRepository
from backend.app.models.users import User, UserRole


class BookingService:
    def __init__(self, booking_repository: BookingRepository, room_repository: RoomsRepository,
                  hostel_repository: HostelRepository):
        self.booking_repository = booking_repository
        self.room_repository = room_repository
        self.hostel_repository = hostel_repository

# working +
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
            # update room availability
            self.room_repository.update_room_availability_status(data.room_id)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Room is already full")

        booking = Booking(
            first_name=data.first_name,
            last_name=data.last_name,
            email_address=data.email_address,
            phone_number=data.phone_number,
            university=data.university,
            hostel_id=data.hostel_id,
            room_id=data.room_id,
            status=BookingStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.booking_repository.create_booking(booking)

        # Increment room occupancy count after successful booking
        self.room_repository.increment_room_occupancy(booking.room_id)

        # TODO: Send Email notification for the booking

        return JSONResponse("Booking received successfully waiting for approval and payment.")

# working +
    async def get_all_room_booking_for_one_owner(self, current_user: User) -> dict:
        # Authorization check
        if current_user.role != UserRole.HOSTEL_OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to view room bookings"
            )

        # Fetch owned hostels
        owned_hostels = self.hostel_repository.get_all_hostels_by_one_owner(current_user.id)
        # if not owned_hostels:
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN,
        #         detail="User does not own any hostels."
        #     )

        result = {"hostels": []}

        for hostel in owned_hostels:
            bookings = self.booking_repository.get_all_room_booking_by_hostel_id(hostel.id)

            booking_list = [
                BookingResponseSchema(
                    id=booking.id,
                    first_name=booking.first_name,
                    last_name=booking.last_name,
                    email_address=booking.email_address,
                    phone_number=booking.phone_number,
                    university=booking.university,
                    hostel_id=booking.hostel_id,
                    room_id=booking.room_id,
                    status=booking.status,
                    created_at=booking.created_at,
                    updated_at=booking.updated_at,
                )
                for booking in bookings
            ]

            result["hostels"].append({
                "hostel_id": hostel.id,
                "hostel_name": hostel.name,
                "bookings": booking_list
            })

        return result