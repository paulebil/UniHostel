from fastapi import APIRouter, Depends, status

from backend.app.repository.hostels import HostelRepository
from backend.app.repository.custodian import HostelOwnerRepository
from backend.app.services.rooms import RoomService
from backend.app.repository.rooms import RoomsRepository
from backend.app.schemas.rooms import *
from backend.app.responses.rooms import *

from backend.app.core.security import Security
from backend.app.database.database import get_session

from sqlalchemy.orm import Session

security = Security()

room_router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(security.get_current_user)]
)

room_user_router = APIRouter(
    prefix="/rooms",
    tags=["Students"],
    responses={404: {"description": "Not found"}},
)

def get_rooms_service(session: Session = Depends(get_session)) -> RoomService:
    room_repository = RoomsRepository(session)
    hostel_repository = HostelRepository(session)
    hostel_owner_repository = HostelOwnerRepository(session)
    return RoomService(room_repository, hostel_repository, hostel_owner_repository)

@room_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=RoomResponse)
async def create_room(data: RoomCreateSchema, room_service: RoomService = Depends(get_rooms_service),
                      current_user = Depends(security.get_current_user)):
    return await room_service.create_room(data, current_user)

@room_router.put("/update", status_code=status.HTTP_200_OK, response_model=RoomResponse)
async def update_room(data: RoomUpdateSchema, room_service: RoomService = Depends(get_rooms_service),
                      current_user = Depends(security.get_current_user)):
    return await room_service.update_room(data, current_user)

@room_router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_room(data: DeleteRoomSchema, room_service: RoomService = Depends(get_rooms_service),
                      current_user = Depends(security.get_current_user)):
    return await room_service.delete_room(data, current_user)

@room_router.get("/get-all-my-rooms", status_code=status.HTTP_200_OK, response_model=AllRoomsResponse)
async def get_all_my_rooms(hostel_id: int, room_service: RoomService = Depends(get_rooms_service), current_user = Depends(security.get_current_user)):
    return await room_service.get_all_rooms_by_hostel_id_custodian(hostel_id, current_user)

@room_user_router.get("/get-all-rooms", status_code=status.HTTP_200_OK, response_model=AllRoomsResponse)
async def get_all_rooms_in_a_hostel(hostel_id: int, room_service: RoomService = Depends(get_rooms_service)):
    return await room_service.get_all_rooms_by_hostel_id(hostel_id)

@room_user_router.get("/get-single-room", status_code=status.HTTP_200_OK, response_model=RoomResponse)
async def get_single_room_detail(hostel_id: int, room_number: str, room_service: RoomService = Depends(get_rooms_service)):
    return await room_service.get_single_room_by_hostel_id(room_number, hostel_id)
