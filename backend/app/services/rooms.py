from fastapi import HTTPException, status

from backend.app.models.hostels import Rooms
from backend.app.repository.rooms import RoomsRepository
from backend.app.schemas.rooms import *
from backend.app.responses.rooms import *

from backend.app.repository.hostels import HostelRepository
from backend.app.repository.custodian import HostelOwnerRepository

from backend.app.models.users import User


class RoomService:
    def __init__(self, rooms_repository: RoomsRepository, hostel_repository: HostelRepository,
                 owner_repo: HostelOwnerRepository):
        self.hostel_owner_repository = owner_repo
        self.rooms_repository = rooms_repository
        self.hostel_repository = hostel_repository

    async def create_room(self, data: RoomCreateSchema, current_user: User) -> RoomResponse:
        # Authorization check
        if not current_user.hostel_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not authorized to create a room")

        # Fetch hostel owner
        owner = self.hostel_owner_repository.get_hostel_owner_by_user_id(current_user.id)
        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User is not registered as a hostel owner")

        # Fetch owned hostels
        owned_hostels = self.hostel_repository.get_all_hostels_by_one_owner(owner.id)
        if not owned_hostels:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User does not own any hostel to create a room")

        # Validate hostel ownership
        hostel_ids = {hostel.id for hostel in owned_hostels}  # Fast lookup
        if data.hostel_id not in hostel_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="You can only create rooms for hostels you own")

        # Check if room number already exists
        room_exists = self.rooms_repository.get_room_by_room_number(data.room_number)
        if room_exists:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Room with this number already exists.")

        # Create room instance
        room = Rooms(
            hostel_id=data.hostel_id,
            room_number=data.room_number,
            price_per_semester=data.price_per_semester,
            room_type=data.room_type,
            availability=data.availability,
            capacity=data.capacity,
            bathroom=data.bathroom,
            balcony=data.balcony,
            image_url=data.image_url,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Save room to database
        self.rooms_repository.create_room(room)

        # Return response
        return RoomResponse(
            id=room.id,
            hostel_id=room.hostel_id,
            room_number=room.room_number,
            price_per_semester=room.price_per_semester,
            room_type=room.room_type.value,  # Convert Enum to string
            availability=room.availability,
            capacity=room.capacity,
            bathroom=room.bathroom,
            balcony=room.balcony,
            image_url=room.image_url,
            created_at=room.created_at,
            updated_at=room.updated_at
        )


    async def get_all_rooms(self) -> AllRoomsResponse:
        rooms =  self.rooms_repository.get_all_rooms()

        if not rooms:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Rooms not found")

        rooms_response = [
            RoomResponse(
                id=room.id,
                hostel_id=room.hostel_id,
                room_number=room.room_number,
                price_per_semester=room.price_per_semester,
                room_type=room.room_type.value,  # Convert Enum to string
                availability=room.availability,
                capacity=room.capacity,
                bathroom=room.bathroom,
                balcony=room.balcony,
                image_url=room.image_url,
                created_at=room.created_at,
                updated_at=room.updated_at
            ) for room in rooms
        ]

        return AllRoomsResponse(rooms=rooms_response)