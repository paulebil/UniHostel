from fastapi import HTTPException, status

from backend.app.models.hostels import Hostel
from backend.app.models.users import User
from backend.app.repository.hostels import HostelRepository
from backend.app.schemas.hostels import *
from backend.app.responses.hostels import *


class HostelService:
    def __init__(self, hostel_repository: HostelRepository):
        self.hostel_repository = hostel_repository

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
