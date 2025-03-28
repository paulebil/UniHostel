from fastapi import APIRouter, Depends, status

from backend.app.repository.booking import BookingRepository
from backend.app.repository.rooms import RoomsRepository
from backend.app.services.booking import BookingService
from backend.app.responses.booking import *
from backend.app.schemas.booking import *

from backend.app.core.security import Security
from backend.app.database.database import get_session

from sqlalchemy.orm import Session

booking_user_router = APIRouter(
    prefix="/booking",
    tags=["Students"],
    responses={404: {"description": "Not found"}},
)
def get_booking_service(session: Session = Depends(get_session)) -> BookingService:
    booking_repository = BookingRepository(session)
    room_repository = RoomsRepository(session)
    return BookingService(booking_repository, room_repository)

@booking_user_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=BookingResponseSchema)
async def create_booking(data: BookingCreateSchema, booking_service: BookingService = Depends(get_booking_service)):
    return await booking_service.create_booking(data)

@booking_user_router.put("/update", status_code=status.HTTP_200_OK, response_model=BookingResponseSchema)
async def update_booking(data: BookingUpdateSchema, booking_service: BookingService = Depends(get_booking_service)):
    return await booking_service.update_booking(data)
