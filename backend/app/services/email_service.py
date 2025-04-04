from fastapi import BackgroundTasks
from backend.app.core.config import get_settings
from backend.app.models.users import User
from backend.app.core.email_config import send_email, send_email_with_attachment
from backend.app.utils.email_context import USER_VERIFY_ACCOUNT, FORGOT_PASSWORD
from backend.app.core.security import Security


from backend.app.utils.s3minio.minio_client import  download_receipt_file_from_minio

security = Security()
settings = get_settings()


class UserAuthEmailService:
    """
      UserAuthEmailService is a stateless utility class that handles email sending.

      Why is this class stateless?
      - It does not store or modify any state; it only sends emails.
      - It does not require dependency injection (e.g., it directly uses `settings` and `send_email`).
      - Using @staticmethod makes it easier to use without instantiation, keeping the code clean.

      Alternative Approach:
      - If we needed to inject an email provider dynamically, we could make this class stateful
        and pass configurations during initialization.
      """

    @staticmethod
    async def send_account_verification_email(user: User, background_task: BackgroundTasks):
        string_context = user.get_context_string(context=USER_VERIFY_ACCOUNT)
        token = security.hash_password(string_context)
        activate_url = f"{settings.FRONTEND_HOST}/auth/account-verify?token={token}&email={user.email}"

        data = {
            "app_name": settings.APP_NAME,
            "name": user.name,
            "activate_url": activate_url
        }

        subject = f"Account Verification - {settings.APP_NAME}"

        await send_email(
            recipients=[user.email],
            subject=subject,
            template_name="users/account-verification.html",
            context=data,
            bg_task=background_task
        )

    @staticmethod
    async def send_account_activation_confirmation_email(user: User, background_task: BackgroundTasks):
        data = {
            "app_name": settings.APP_NAME,
            "name": user.name,
            "login_url": f"{settings.FRONTEND_HOST}"
        }

        subject = f"Welcome - {settings.APP_NAME}"

        await send_email(
            recipients=[user.email],
            subject=subject,
            template_name="users/account-verification-confirmation.html",
            context=data,
            bg_task=background_task
        )

    @staticmethod
    async def send_password_reset_email(user: User, background_tasks: BackgroundTasks):
        string_context = user.get_context_string(context=FORGOT_PASSWORD)
        token = security.hash_password(string_context)
        reset_url = f"{settings.FRONTEND_HOST}/reset-password?token={token}&email={user.email}"

        data = {
            "app_name": settings.APP_NAME,
            "name": user.name,
            "activate_url": reset_url
        }

        subject = f"Reset Password - {settings.APP_NAME}"

        await send_email(
            recipients=[user.email],
            subject=subject,
            template_name="users/password-reset.html",
            context=data,
            bg_task=background_tasks
        )

    @staticmethod
    async def send_receipt_email(user_email: str, background_tasks: BackgroundTasks, bucket: str, file_name: str):

        print("Reached Sending email Part")
        data = {
            "app_name": settings.APP_NAME,
            "name": user_email.split("@")[0],  # Optional: extract name
            "message": "Thank you for your payment. Please find your receipt attached."
        }

        attachment = download_receipt_file_from_minio(bucket, file_name)

        if attachment.get("error"):
            # Handle error - you can raise an exception or log the error
            print(attachment["message"])
        else:
            # Proceed with sending the email as attachment
            await send_email_with_attachment(
                recipients=[user_email],
                subject="Your Payment Receipt",
                template_name="payment/receipt.html",
                context=data,
                bg_task=background_tasks,
                attachments=[attachment]
            )


        print("Email sent successfully")