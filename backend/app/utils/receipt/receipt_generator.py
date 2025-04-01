import jinja2
import pdfkit
from datetime import datetime


# Define item fields for the invoice



# Create a context dictionary to pass the data to the Jinja template

context = {
    "receipt_number": "UH-2025001",
    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

    # Booking Details
    "hostel_name": "Sunrise Hostel",
    "room_number": "B-205",
    "duration": 6,
    "status": "CONFIRMED",

    # Student Information
    "student_name": "John Doe",
    "student_email": "john.doe@example.com",
    "student_phone": "+256 770 123456",
    "student_university": "Makerere University",
    "student_course": "Computer Science",
    "student_study_year": "Year 2",

    # Home Residence
    "home_address": "123 Kampala Road",
    "home_district": "Kampala",
    "home_country": "Uganda",

    # Next of Kin
    "next_of_kin_name": "Jane Doe",
    "next_of_kin_phone": "+256 771 654321",
    "kin_relationship": "Sister",

    # Pricing
    "room_price_per_month": 150,
    "total_rent": 150 * 6,  # 6 months rent
    "security_deposit": 100,
    "utility_fees": 50,

    # Payment Info
    "tax_percentage": 5,
    "tax_amount": (150 * 6 + 100 + 50) * 0.05,
    "net_total": (150 * 6 + 100 + 50),
    "total_paid": (150 * 6 + 100 + 50) * 1.05,

    "payment_method": "Mobile Money",
    "transaction_id": "TXN123456789"
}

# Load the Html template using Jinja2

def generate_receipt_pdf(context):

    template_loader = jinja2.FileSystemLoader('./')
    template_env = jinja2.Environment(loader=template_loader)


    # Load the specific template file
    template = template_env.get_template("receipt.html")


    # Render the template with the provided context
    output_text = template.render(context)

    # configure pdfkit with the path to wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")    # get this from the docker container

    # Generate the PDF from the rendered HTML template and apply a CSS
    pdfkit.from_string(output_text, 'generated_receipt.pdf', configuration=config,
               css="/home/ebilpaul/PycharmProjects/UniHostel/backend/app/utils/receipt/styles.css")

    print("Receipt PDF generated successfully!")

