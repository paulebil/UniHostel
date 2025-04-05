from fastapi import BackgroundTasks
from datetime import datetime

import jinja2
import pdfkit
import os
import uuid

from backend.app.utils.s3minio.minio_client import upload_file_to_minio

from backend.app.repository.receipt import ReceiptRepository
from backend.app.models.receipt import Receipt
from backend.app.schemas.receipts import ReceiptStatus, ReceiptContext


def generate_receipt_pdf(context: ReceiptContext, bucket_name , receipt_repository: ReceiptRepository):

    # Generate unique file name
    # unique_id = str(uuid.uuid4())
    pdf_filename = f"{context.receipt_number}.pdf"
    pdf_path = f"pdfs/{pdf_filename}"
    content_type = "application/pdf"

    # Define the absolute path to the templates folder
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMPLATE_DIR = os.path.join(BASE_DIR, "../../templates")  # Adjust as needed

    # Load the template from the correct directory
    template_loader = jinja2.FileSystemLoader(TEMPLATE_DIR)
    template_env = jinja2.Environment(loader=template_loader)

    # Load the specific template file
    template = template_env.get_template("receipt.html")

    # Render the template with the provided context
    output_text = template.render(context)

    # Configure pdfkit with the path to wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")  # Ensure this path is correct

    # Path to CSS file
    CSS_PATH = os.path.join(BASE_DIR, "styles.css")  # Adjust path if necessary

    # Generate the PDF from the rendered HTML template
    pdfkit.from_string(output_text, pdf_path, configuration=config, css=CSS_PATH)

    # Step 1: Create receipt record (Initial Status: PENDING)
    receipt_metadata = Receipt(
        status=ReceiptStatus.PENDING.value,
        file_name=pdf_filename,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    receipt_id = receipt_repository.create_receipt_metadata(receipt_metadata)

    try:
        # Step 2: Upload receipt to MinIO
        result = upload_file_to_minio(bucket_name, pdf_filename, pdf_path, content_type)

       # print(f"Bucket: {result.bucket_name}, Object: {result.object_name}, Version: {result.version_id}, ETag: {result.etag}")

        # Step 3: Fetch the receipt from DB before updating
        receipt_record = receipt_repository.get_receipt_metadata_by_id(receipt_id)

        if receipt_record:
            receipt_record.status = ReceiptStatus.COMPLETED.value
            receipt_record.bucket_name = result.bucket_name
            receipt_record.object_name = result.object_name
            receipt_record.version_id = result.version_id
            receipt_record.etag = result.etag
            receipt_record.updated_at = datetime.now()

        else:
            print(f"Error: Receipt with ID {receipt_id} not found!")
            return

    except Exception as e:
        print(f"Error uploading to MinIO: {str(e)}")

        # If upload fails, fetch receipt and mark as FAILED
        receipt_record = receipt_repository.get_receipt_metadata_by_id(receipt_id)

        if receipt_record:
            receipt_record.status = ReceiptStatus.FAILED.value
            receipt_record.updated_at = datetime.now()
        else:
            print(f"Error: Receipt with ID {receipt_id} not found!")
            return

    # Step 4: Save updated receipt record
    receipt_repository.update_receipt_metadata(receipt_record)

   # print("Receipt updated successfully!")

    # Step 5: Remove the generated PDF
    #print(f"Removing the pdf: {pdf_path}")
    os.remove(pdf_path)


def generate_receipt_background(background_tasks: BackgroundTasks, context, bucket_name, receipt_repository: ReceiptRepository):
    background_tasks.add_task(generate_receipt_pdf, context, bucket_name, receipt_repository)
    return {"message": "Receipt generation started."}


# TODO: Turn these functions to async

