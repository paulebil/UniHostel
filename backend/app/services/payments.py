from fastapi import HTTPException, status

from datetime import datetime

from starlette.responses import JSONResponse

from backend.app.repository.payments import PaymentRepository
from backend.app.models.payments import Payment
from backend.app.responses.payments import *
from backend.app.schemas.payments import *

from backend.app.repository.booking import BookingRepository
from backend.app.repository.rooms import RoomsRepository



class PaymentService:
    def __init__(self, payment_repository: PaymentRepository, booking_repository: BookingRepository,
                 room_repository: RoomsRepository):
        self.payment_repository = payment_repository
        self.booking_repository = booking_repository
        self.room_repository = room_repository

    async def create_payment(self, data: PaymentCreate):

        booking_info = self.booking_repository.get_booking_by_booking_id(data.booking_id)
        if not booking_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking with this id does not exist.")

        room_info = self.room_repository.get_room_by_id(booking_info.room_id)
        if not room_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room with this id does not exist.")
        if room_info.booked_status:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Room is already booked")

        payments_info = self.payment_repository.get_payment_by_transaction_id(data.transaction_id)

        if payments_info:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Payment can not have the same transaction id.")

        payment = Payment(
            booking_id=data.booking_id,
            amount=data.amount,
            payment_status=data.payment_status.value,
            transaction_id=data.transaction_id,
            payment_method=data.payment_method,

            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self.payment_repository.make_payment(payment)

        # check for transaction id in database and validate it

        # update payment status to completed

        # create receipt with payment info

        # TODO: Send email with the receipt

        return JSONResponse("Payment received successfully, check your email for the receipt")
