import jinja2
import pdfkit
from datetime import datetime


# Define item fields for the invoice



# Create a context dictionary to pass the data to the Jinja template

context = {}

# Load the Html template using Jinja2

template_loader = jinja2.FileSystemLoader('./')
template_env = jinja2.Environment(loader=template_loader)


# Load the specific template file
template = template_env.get_template("receipt.html")


# Render the template with the provided context
output_text = template.render(context)

# configure pdfkit with the path to wkhtmltopdf
config = pdfkit.configuration(wkhtmltopdf="")    # get this from the docker container

# Generate the PDF from the rendered HTML template and apply a CSS
pdfkit.from_string(output_text, 'generated_receipt.pdf', configuration=config, css="receipt_style.css")
