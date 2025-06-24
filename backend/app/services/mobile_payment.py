from fastapi import HTTPException, status, BackgroundTasks
from starlette.responses import JSONResponse
from datetime import datetime
import uuid

from backend.app.models.mobile_payment  import Payment,PaymentStatus
from backend.app.schemas.mobile_payment import  CardDetails, MobileMoneyDetails, PaymentCreate
from backend.app.repository.payments import PaymentRepository
from backend.app.repository.transactions import TransactionRepository
from backend.app.repository.hostels import HostelRepository
from backend.app.repository.rooms import RoomsRepository
from backend.app.repository.receipt import ReceiptRepository
from backend.app.schemas.receipts import ReceiptContext
from backend.app.utils.receipt.receipt_generator import generate_receipt_background
from backend.app.services.email_service import UserAuthEmailService
from backend.app.core.config import get_settings

settings = get_settings()

class MobilePaymentService:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        room_repository: RoomsRepository,
        hostel_repository: HostelRepository,
        transaction_repository: TransactionRepository,
        receipt_repository: ReceiptRepository
    ):
        self.payment_repository = payment_repository
        self.room_repository = room_repository
        self.hostel_repository = hostel_repository
        self.transaction_repository = transaction_repository
        self.receipt_repository = receipt_repository

    async def create_payment(self, data: PaymentCreate, background_tasks: BackgroundTasks):
        room = self.room_repository.get_room_by_id(data.room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")

        hostel = self.hostel_repository.get_hostel_by_id(data.hostel_id)
        if not hostel:
            raise HTTPException(status_code=404, detail="Hostel not found")

        # 🚫 No transaction_id from client — generate one internally
        generated_transaction_id = str(uuid.uuid4())

        # Prepare payment object
        payment = Payment(
            hostel_id=data.hostel_id,
            room_id=data.room_id,
            amount=data.amount,
            payment_status=PaymentStatus.COMPLETED,  # immediately mark as complete
            transaction_id=generated_transaction_id,
            payment_method=data.payment_method,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        if data.card_details:
            payment.card_details = CardDetails(**data.card_details.model_dump())
        elif data.mobile_money_details:
            payment.mobile_money_details = MobileMoneyDetails(**data.mobile_money_details.model_dump())

        payment_id = self.payment_repository.make_payment(payment)

        # 🧾 Generate receipt
        receipt_context = ReceiptContext(
            receipt_number=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            hostel_name=hostel.name,
            room_number=room.room_number,
            duration=0,
            status="Paid",
            student_name="Anonymous",
            student_email="example@student.com",
            student_phone="0000000000",
            student_course="Unknown",
            student_study_year="Unknown",
            student_university="Unknown",
            room_price_per_semester=room.price_per_semester,
            transaction_id=generated_transaction_id,  # still include it in receipt if useful
            security_deposit=payment.amount,
            payment_method = str(payment.payment_method)
        )

        generate_receipt_background(background_tasks, receipt_context, settings.MINIO_PDF_BUCKET_NAME,
                                    self.receipt_repository)

        await UserAuthEmailService.send_receipt_email_with_link(
            receipt_context.student_email,
            background_tasks,
            settings.MINIO_PDF_BUCKET_NAME,
            f"{receipt_context.receipt_number}.pdf"
        )

        return JSONResponse(content={"message": "Payment received successfully. Receipt sent via email."})
