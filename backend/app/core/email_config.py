from pathlib import Path
from fastapi_mail import FastMail, MessageType, MessageSchema, ConnectionConfig
from fastapi.background import BackgroundTasks
from backend.app.core.config import get_settings

settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USERNAME,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_SERVER,
    MAIL_STARTTLS=settings.SMTP_STARTTLS,
    MAIL_SSL_TLS=settings.SMTP_SSL_TLS,
    MAIL_DEBUG=settings.SMTP_DEBUG,
    MAIL_FROM=settings.SMTP_FROM,
    MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
)

fm = FastMail(conf)

async def send_email(recipients: list, subject: str, context: dict, template_name: str, bg_task: BackgroundTasks):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        template_body=context,
        subtype=MessageType.html
    )

    bg_task.add_task(fm.send_message, message, template_name=template_name)