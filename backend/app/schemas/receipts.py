from pydantic import BaseModel, EmailStr, constr
from datetime import datetime

class ReceiptContext(BaseModel):
    # Receipt Information
    receipt_number: constr()  # e.g., "UH-2025001"
    created_at: datetime

    # Booking Details
    hostel_name: str
    room_number: str
    duration: int
    status: str

    # Student Information
    student_name: str
    student_email: EmailStr
    student_phone: str
    student_university: str
    student_course: str
    student_study_year: str

    # Home Residence
    home_address: str
    home_district: str
    home_country: str

    # Next of Kin
    next_of_kin_name: str
    next_of_kin_phone: str
    kin_relationship: str

    # Pricing
    room_price_per_month: float
    total_rent: float
    security_deposit: float
    utility_fees: float
    tax_percentage: float
    tax_amount: float
    net_total: float
    total_paid: float

    # Payment Info
    payment_method: str
    transaction_id: str