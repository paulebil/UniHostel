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

    async def create_room(self, data: RoomCreateSchema, current_user: User):
        # Check if user is a hostel owner
        if current_user.hostel_owner:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not authorized to create a room")

        # Get owner by user id
        # Get hostel by owner id

