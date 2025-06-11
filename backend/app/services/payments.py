from fastapi import HTTPException, status, BackgroundTasks

import uuid

from starlette.responses import JSONResponse

from backend.app.repository.payments import PaymentRepository
from backend.app.models.payments import Payment
from backend.app.responses.payments import *
from backend.app.schemas.payments import *

from backend.app.repository.booking import BookingRepository
from backend.app.repository.rooms import RoomsRepository
from backend.app.repository.transactions import TransactionRepository
from backend.app.repository.hostels import HostelRepository
from backend.app.repository.receipt import ReceiptRepository

from backend.app.schemas.receipts import ReceiptContext

from backend.app.utils.receipt.receipt_generator import generate_receipt_background

from backend.app.services.email_service import UserAuthEmailService

from backend.app.core.config import get_settings

settings = get_settings()



class PaymentService:
    def __init__(self, payment_repository: PaymentRepository, booking_repository: BookingRepository,
                 room_repository: RoomsRepository, transaction_repository: TransactionRepository,
                 hostel_repository:HostelRepository, receipt_repository:ReceiptRepository ):
        self.payment_repository = payment_repository
        self.booking_repository = booking_repository
        self.room_repository = room_repository
        self.transaction_repository = transaction_repository
        self.hostel_repository = hostel_repository
        self.receipt_repository = receipt_repository

    async def create_payment(self, data: PaymentCreate, background_tasks: BackgroundTasks):

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
        payment_id = self.payment_repository.make_payment(payment)

        # check for transaction id in database and validate it(validating that the payment was received to our backend from strip)
        transaction_id = self.transaction_repository.get_transaction_by_id(data.transaction_id)
        if  transaction_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction id not found, payment not received.")

        # update payment status to completed
        payment_to_update = self.payment_repository.get_payment_by_id(payment_id)

        payment_to_update.payment_status = PaymentStatus.COMPLETED.value

        updated_payment_id = self.payment_repository.update_payment(payment_to_update)

        updated_payment = self.payment_repository.get_payment_by_id(updated_payment_id)

        # create receipt with payment info



        hostel_info = self.hostel_repository.get_hostel_by_id(booking_info.hostel_id)
        if not hostel_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel not found.")

        unique_id = str(uuid.uuid4())

        receipt_context = ReceiptContext(
            # Receipt information
            receipt_number=unique_id,
            created_at=datetime.now(),

            # Booking Details
            hostel_name=hostel_info.name,
            room_number=room_info.room_number,
            duration=0,
            status=booking_info.status,

            # Student information
            student_name=booking_info.student_name,
            student_email=booking_info.student_email,
            student_phone=booking_info.student_phone,
            student_course=booking_info.student_course,
            student_study_year=booking_info.student_study_year,
            student_university=booking_info.student_university,

            # Pricing
            room_price_per_semester=room_info.price_per_semester,

            # Payment information
            payment_method=updated_payment.payment_method,
            transaction_id=updated_payment.transaction_id,
            security_deposit=updated_payment.amount
        )

        bucket_name = settings.MINIO_PDF_BUCKET_NAME

        generate_receipt_background(background_tasks, receipt_context, bucket_name, self.receipt_repository)

        # TODO: Send email with the receipt

        await UserAuthEmailService.send_receipt_email_with_link(receipt_context.student_email, background_tasks, bucket_name, f"{receipt_context.receipt_number}.pdf")

        return JSONResponse("Payment received successfully, check your email for the receipt")
