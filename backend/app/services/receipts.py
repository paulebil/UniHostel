from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks

from backend.app.utils.receipt.receipt_generator import generate_receipt_background
from backend.app.schemas.receipts import ReceiptContext
from backend.app.repository.receipt import ReceiptRepository


from backend.app.repository.booking import BookingRepository
from backend.app.repository.rooms import RoomsRepository
from backend.app.repository.hostels import HostelRepository
from backend.app.repository.payments import PaymentRepository

from backend.app.core.config import get_settings

settings = get_settings()


class ReceiptService:

    def __init__(self, booking_repository: BookingRepository, room_repository: RoomsRepository,
                hostel_repository: HostelRepository, receipt_repository: ReceiptRepository,
                 payment_repository: PaymentRepository):
        self.hostel_repository = hostel_repository
        self.booking_repository = booking_repository
        self.room_repository = room_repository
        self.receipt_repository = receipt_repository
        self.payment_repository = payment_repository

    async def create_receipt(self, booking_id: int, background_tasks: BackgroundTasks):
        booking_data = self.booking_repository.get_booking_by_booking_id(booking_id)

        room_info = self.room_repository.get_room_by_id(booking_data.room_id)

        hostel_info = self.hostel_repository.get_hostel_by_id(booking_data.hostel_id)

        payment_info = self.payment_repository.get_payment_by_booking_id(booking_id)

        receipt_context = ReceiptContext(
            # Receipt information
            receipt_number="",
            created_at=datetime.now(),

            # Booking Details
            hostel_name=hostel_info.name,  ## check this
            room_number=room_info.room_number,
            duration=0,
            status=booking_data.status,

            # Student Information
            student_name=booking_data.student_name,
            student_email=booking_data.student_email,
            student_phone=booking_data.student_phone,
            student_course=booking_data.student_course,
            student_study_year=booking_data.student_study_year,
            student_university=booking_data.student_university,

            # Home Residence
            home_address=booking_data.home_address,
            home_district=booking_data.home_district,
            home_country=booking_data.home_country,

            # Next of kin
            next_of_kin_name=booking_data.next_of_kin_name,
            next_of_kin_phone=booking_data.next_of_kin_phone,
            kin_relationship=booking_data.kin_relationship,

            # Pricing
            room_price_per_semester=room_info.price_per_semester,

            # Payment information
            payment_method=payment_info.payment_method,
            transaction_id=payment_info.transaction_id,
            security_deposit = payment_info.amount
        )

        bucket_name = settings.MINIO_PDF_BUCKET_NAME

        # Proceed to generate receipt
        generate_receipt_background(background_tasks, receipt_context, bucket_name, self.receipt_repository)

        # return json
        return JSONResponse("Receipt generated successfully.")
