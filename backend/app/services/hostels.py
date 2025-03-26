from fastapi import HTTPException, status
from starlette.responses import JSONResponse

from backend.app.models.hostels import Hostel
from backend.app.models.users import User
from backend.app.repository.hostels import HostelRepository
from backend.app.schemas.hostels import *
from backend.app.responses.hostels import *

from backend.app.repository.custodian import HostelOwnerRepository



class HostelService:
    def __init__(self, hostel_repository: HostelRepository, hostel_owner_repository: HostelOwnerRepository ):
        self.hostel_repository = hostel_repository
        self.hostel_owner_repository = hostel_owner_repository

    async def create_hostel(self, data: HostelCreateSchema, current_user: User):
        # check if user is a hostel owner
        if not current_user.hostel_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not authorized to create a hostel.")
        # check if Hostel with this name exists
        hostel_exists = self.hostel_repository.get_hostel_by_name(data.name)
        if hostel_exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A hostel with this name already exist.")
        # create hostel
        hostel = Hostel(
            name=data.name,
            image_url=data.image_url,
            description=data.description,
            location=data.location,
            owner_id=current_user.id,
            average_price=data.average_price,
            available_rooms=data.available_rooms,
            amenities=data.amenities,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.hostel_repository.create_hostel(hostel)

        # Return hostel response
        hostel_response = HostelResponse(
            id=hostel.id,
            name=hostel.name,
            image_url=hostel.image_url,
            description=hostel.description,
            location=hostel.location,
            owner_id=hostel.owner_id,
            average_price=hostel.average_price,
            available_rooms=hostel.available_rooms,
            amenities=hostel.amenities,
            created_at=hostel.created_at,
            updated_at=hostel.updated_at
        )
        return hostel_response

    async def update_hostel(self, data: HostelUpdateSchema, current_user: User):
        # check if user is a hostel owner
        if not current_user.hostel_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User is not authorized to update a hostel.")
        # Retrieve the owner using user id
        owner = self.hostel_owner_repository.get_hostel_owner_by_user_id(current_user.id)
        if not owner:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,  detail="Hostel owner not found.")

        # get the hostel by owner id
        hostel = self.hostel_repository.get_hostel_by_owner_id(owner.id)

        if not hostel:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,  detail="Hostel by this owner does not exists.")

        # Update hostel
        if data.name:
            hostel.name = data.name
        if data.location:
            hostel.location = data.location
        if data.amenities:
            hostel.amenities = data.amenities
        if data.available_rooms is not None:  # Check if available_rooms is explicitly set
            hostel.available_rooms = data.available_rooms
        if data.average_price:
            hostel.average_price = data.average_price
        if data.description:
            hostel.description = data.description
        if data.image_url:
            hostel.image_url = data.image_url
        self.hostel_repository.update_hostel(hostel)

        return HostelResponse(
            id=hostel.id,
            name=hostel.name,
            image_url=hostel.image_url,
            description=hostel.description,
            location=hostel.location,
            owner_id=hostel.owner_id,
            average_price=hostel.average_price,
            available_rooms=hostel.available_rooms,
            amenities=hostel.amenities,
            created_at=hostel.created_at,
            updated_at=hostel.updated_at,
        )

    async def delete_hostel(self, hostel_id: int, current_user: User):
        # check if user is a hostel owner
        if not current_user.hostel_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="User is not authorized to delete a hostel.")
        # Retrieve the owner using user id
        owner = self.hostel_owner_repository.get_hostel_owner_by_user_id(current_user.id)
        if not owner:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,  detail="Hostel owner not found.")

        # get the hostels by owner id
        hostel = self.hostel_repository.get_hostel_by_owner_id(owner.id)
        if not hostel:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,  detail="Hostel by this owner does not exists.")

        hostel_to_delete = self.hostel_repository.get_hostel_by_id(hostel_id)
        if not hostel_to_delete:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hostel does not exists")

        self.hostel_repository.delete_hostel(hostel_to_delete)

        return JSONResponse("Hostel deleted successfully.")



    async def get_all_hostels(self) -> HostelListResponse:
        hostels =  self.hostel_repository.get_all_hostels()
        # Convert each hostel (SQLAlchemy object) into HostelResponse
        hostel_responses = [
            HostelResponse(
                id=hostel.id,
                name=hostel.name,
                image_url=hostel.image_url,
                description=hostel.description,
                location=hostel.location,
                owner_id=hostel.owner_id,
                average_price=hostel.average_price,
                available_rooms=hostel.available_rooms,
                amenities=hostel.amenities,
                created_at=hostel.created_at,
                updated_at=hostel.updated_at,
            )
            for hostel in hostels
        ]

        # Return a single HostelListResponse with the list of HostelResponse
        return HostelListResponse(hostels=hostel_responses)
