from fastapi import APIRouter, Depends, status
from fastapi import BackgroundTasks

from backend.app.repository.booking import BookingRepository
from backend.app.repository.rooms import RoomsRepository
from backend.app.repository.receipt import ReceiptRepository
from backend.app.repository.custodian import HostelOwnerRepository
from backend.app.repository.hostels import HostelRepository
from backend.app.repository.payments import PaymentRepository
from backend.app.repository.transactions import TransactionRepository

from backend.app.services.payments import PaymentService
from backend.app.schemas.payments import *
from backend.app.responses.payments import *
from backend.app.services.booking import BookingService
from backend.app.responses.booking import *
from backend.app.schemas.booking import *

from backend.app.core.security import Security
from backend.app.database.database import get_session

from backend.app.services.receipts import ReceiptService

from typing import List

from sqlalchemy.orm import Session

security = Security()

booking_user_router = APIRouter(
    prefix="/booking",
    tags=["Students"],
    responses={404: {"description": "Not found"}},
)

booking_router = APIRouter(
    prefix="/booking/custodians",
    tags=["Custodians"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(security.get_current_user)]
)


def get_booking_service(session: Session = Depends(get_session)) -> BookingService:
    booking_repository = BookingRepository(session)
    room_repository = RoomsRepository(session)
    hostel_owner_repository = HostelOwnerRepository(session)
    hostel_repository = HostelRepository(session)
    return BookingService(booking_repository, room_repository, hostel_owner_repository, hostel_repository)

@booking_user_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_booking(data: BookingCreateSchema, booking_service: BookingService = Depends(get_booking_service)):
    return await booking_service.create_booking(data)
#
# @booking_user_router.put("/update", status_code=status.HTTP_200_OK, response_model=BookingResponseSchema)
# async def update_booking(data: BookingUpdateSchema, booking_service: BookingService = Depends(get_booking_service)):
#     return await booking_service.update_booking(data)
#
# @booking_user_router.delete("/cancel", status_code=status.HTTP_200_OK )
# async def cancel_booking(booking_id: int, booking_service: BookingService = Depends(get_booking_service)):
#     return await booking_service.cancel_booking(booking_id)
#
# @booking_user_router.get("/booking", status_code=status.HTTP_200_OK, response_model=BookingResponseSchema)
# async def get_booking_by_id(booking_id: int, booking_service: BookingService = Depends(get_booking_service)):
#     return await booking_service.get_booking_by_id(booking_id)
#
# @booking_user_router.get("/bookings", status_code=status.HTTP_200_OK, response_model=List[BookingResponseSchema])
# async def get_all_my_bookings(email: str, booking_service: BookingService = Depends(get_booking_service)):
#     return await booking_service.get_all_my_bookings(email)
#
# @booking_router.get("/bookings", status_code=status.HTTP_200_OK, response_model=List[BookingResponseSchema])
# async def get_all_bookings_for_hostel(hostel_id: int, booking_service: BookingService = Depends(get_booking_service),
#                                       current_user = Depends(security.get_current_user)):
#     return await booking_service.get_all_room_booking_by_hostel(hostel_id, current_user)
#
# @booking_router.get("/booking", status_code=status.HTTP_200_OK, response_model=BookingResponseSchema)
# async def get_single_booking_for_hostel(hostel_id: int, booking_id: int, booking_service: BookingService = Depends(get_booking_service),
#                                         current_user = Depends(security.get_current_user)):
#     return await booking_service.get_one_room_booking_for_hostel(hostel_id, booking_id, current_user)


def get_receipt_service(session: Session = Depends(get_session)) -> ReceiptService:
    booking_repository = BookingRepository(session)
    room_repository = RoomsRepository(session)
    hostel_repository = HostelRepository(session)
    receipt_repository = ReceiptRepository(session)
    payment_repository = PaymentRepository(session)
    return ReceiptService(booking_repository, room_repository, hostel_repository, receipt_repository, payment_repository)


# @booking_user_router.get("/receipt", status_code=status.HTTP_200_OK)
# async def get_booking_receipt(booking_id: int, background_tasks: BackgroundTasks, receipt_service: ReceiptService = Depends(get_receipt_service)):
#     return await receipt_service.create_receipt(booking_id, background_tasks )


def get_payment_service(session: Session = Depends(get_session)) -> PaymentService:
    payment_repository = PaymentRepository(session)
    booking_repository = BookingRepository(session)
    room_repository = RoomsRepository(session)
    hostel_repository = HostelRepository(session)
    transaction_repository = TransactionRepository(session)
    receipt_repository = ReceiptRepository(session)

    return PaymentService(payment_repository, booking_repository, room_repository, transaction_repository, hostel_repository, receipt_repository)


@booking_user_router.post("/payment", status_code=status.HTTP_200_OK)
async def make_payment(data: PaymentCreate, background_tasks: BackgroundTasks,payment_service: PaymentService = Depends(get_payment_service)):
    return await payment_service.create_payment(data, background_tasks)
