from fastapi import BackgroundTasks

import jinja2
import pdfkit
import os
import uuid
from backend.app.utils.s3minio.minio_client import upload_file_to_minio


def generate_receipt_pdf(context, bucket_name):

    # Generate unique file name
    unique_id = str(uuid.uuid4())
    pdf_filename = f"{unique_id}.pdf"
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

    print("Receipt PDF generated successfully!")

    result = upload_file_to_minio(bucket_name, pdf_filename, pdf_path, content_type)

    print(f" Bucket name: {result.bucket_name}; Object name: {result.object_name} Object version: {result.version_id}; Object etag: {result.etag}")

    print(f"Removing the pdf: {pdf_path}")
    os.remove(pdf_path)

    return result
