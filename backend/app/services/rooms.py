from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from backend.app.models.hostels import Room
from backend.app.repository.rooms import RoomsRepository
from backend.app.schemas.rooms import *
from backend.app.responses.rooms import *

from backend.app.repository.hostels import HostelRepository
from backend.app.repository.custodian import HostelOwnerRepository

from backend.app.models.images import ImageMetaData
from backend.app.repository.images import ImageMetaDataRepository
from backend.app.responses.images import Images
from backend.app.utils.s3minio.minio_client import  generate_presigned_url

from backend.app.models.users import User


class RoomService:
    def __init__(self, rooms_repository: RoomsRepository, hostel_repository: HostelRepository,
                 owner_repo: HostelOwnerRepository, image_repo: ImageMetaDataRepository):
        self.hostel_owner_repository = owner_repo
        self.rooms_repository = rooms_repository
        self.hostel_repository = hostel_repository
        self.image_repository = image_repo

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
        room = Room(
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

    async def update_room(self, data: RoomUpdateSchema, current_user: User) -> RoomResponse:
        # Authorization check
        if not current_user.hostel_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not authorized to update a room")

        # Fetch hostel owner
        owner = self.hostel_owner_repository.get_hostel_owner_by_user_id(current_user.id)
        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User is not registered as a hostel owner")

        # Fetch owned hostels
        owned_hostels = self.hostel_repository.get_all_hostels_by_one_owner(owner.id)
        if not owned_hostels:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User does not own any hostel")

        # Validate hostel ownership
        hostel_ids = {hostel.id for hostel in owned_hostels}  # Set for fast lookup

        # Get room by room number
        room = self.rooms_repository.get_room_by_room_number(data.room_number)
        if not room or room.hostel_id not in hostel_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Room does not exist or does not belong to one of your hostels.")

        # Update room details (allow False/0 values)
        if data.hostel_id is not None:
            room.hostel_id = data.hostel_id
        if data.room_number is not None:
            room.room_number = data.room_number
        if data.price_per_semester is not None:
            room.price_per_semester = data.price_per_semester
        if data.room_type is not None:
            room.room_type = data.room_type
        if data.availability is not None:
            room.availability = data.availability
        if data.capacity is not None:
            room.capacity = data.capacity
        if data.bathroom is not None:
            room.bathroom = data.bathroom
        if data.balcony is not None:
            room.balcony = data.balcony
        if data.image_url is not None:
            room.image_url = data.image_url

        room.updated_at = datetime.now()

        # Save updates
        self.rooms_repository.update_room(room)

        # Return updated room details
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
    async def delete_room(self, data: DeleteRoomSchema, current_user: User):
        # Authorization check
        if not current_user.hostel_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not authorized to delete a room")

        # Fetch hostel owner
        owner = self.hostel_owner_repository.get_hostel_owner_by_user_id(current_user.id)
        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User is not registered as a hostel owner")

        # Fetch owned hostels
        owned_hostels = self.hostel_repository.get_all_hostels_by_one_owner(owner.id)
        if not owned_hostels:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User does not own any hostel")

        # Validate hostel ownership
        hostel_ids = {hostel.id for hostel in owned_hostels}  # Set for fast lookup

        # Get room by room number and hostel_id
        room = self.rooms_repository.get_room_by_room_number_and_hostel_id(data.room_number, data.hostel_id)
        if not room or room.hostel_id not in hostel_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Room does not exist or does not belong to one of your hostels.")

        # Delete room
        self.rooms_repository.delete_room(room)

        return JSONResponse(content={"message": "Room deleted successfully"}, status_code=status.HTTP_200_OK)


    async def get_all_rooms_by_hostel_id_custodian(self, hostel_id: int, current_user: User):
        # Authorization check
        if not current_user.hostel_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not authorized to view rooms")

        # Fetch hostel owner
        owner = self.hostel_owner_repository.get_hostel_owner_by_user_id(current_user.id)
        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User is not registered as a hostel owner")

        # Fetch owned hostels
        owned_hostels = self.hostel_repository.get_all_hostels_by_one_owner(owner.id)
        if not owned_hostels:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User does not own any hostel")

        # Validate hostel ownership
        hostel_ids = {hostel.id for hostel in owned_hostels}  # Set for fast lookup
        if hostel_id not in hostel_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this hostel")

        # Fetch rooms
        rooms = self.rooms_repository.get_all_rooms_by_hostel_id(hostel_id)
        if not rooms:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No rooms found for this hostel")

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

    async def get_all_rooms_by_hostel_id(self, hostel_id: int) -> AllRoomsResponse:
        rooms =  self.rooms_repository.get_all_rooms_by_hostel_id(hostel_id)

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

    async def get_single_room_by_hostel_id(self, room_number: str, hostel_id: int) -> RoomResponse:
        room = self.rooms_repository.get_room_by_room_number_and_hostel_id(room_number, hostel_id)
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

        # Get all this room image metadata from images table
        images = self.image_repository.get_image_metadata_by_room_id(room.id)
        if not images:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room has no images")

        image_urls = []

        # Get presigned_url for all the images
        for image in images:
            url = generate_presigned_url(image.bucket_name, image.object_name)
            image_urls.append({"url": url})

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
            image_url=image_urls,
            created_at=room.created_at,
            updated_at=room.updated_at
        )

    async def get_single_room_by_hostel_id_custodian(self, room_number: str, hostel_id: int,
                                                     current_user: User) -> RoomResponse:
        # Authorization check: Verify if user is a hostel owner
        if not current_user.hostel_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not authorized to view rooms")

        # Fetch hostel owner from the repository
        owner = self.hostel_owner_repository.get_hostel_owner_by_user_id(current_user.id)
        if not owner:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User is not registered as a hostel owner")

        # Fetch owned hostels
        owned_hostels = self.hostel_repository.get_all_hostels_by_one_owner(owner.id)
        if not owned_hostels:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User does not own any hostel")

        # Validate hostel ownership
        hostel_ids = {hostel.id for hostel in owned_hostels}  # Set for fast lookup
        if hostel_id not in hostel_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this hostel")

        # Fetch the room by room number and hostel ID
        room = self.rooms_repository.get_room_by_room_number_and_hostel_id(room_number, hostel_id)
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

        # Return room details in the response
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
