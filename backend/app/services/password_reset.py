from fastapi import BackgroundTasks, HTTPException

from sqlalchemy.orm import Session

from backend.app.repository.password_reset import PasswordResetRepository
from backend.app.repository.users import UserRepository
from backend.app.services.email_service import send_email
from backend.app.models.users import User
from backend.app.core.config import get_settings
from backend.app.core.security import Security

settings = get_settings()
security = Security()


class PasswordResetService:

    def __init__(self, password_repository: PasswordResetRepository, user_repository: UserRepository):
        self.password_reset_repository = password_repository
        self.user_repository = user_repository


    async def send_password_reset_email(self, user: User, background_tasks: BackgroundTasks):
        """Generate password reset token and send email to the user."""

        string_context = user.get_context_string(context="FORGOT_PASSWORD")

        # Store token in the database
        reset_token = self.password_reset_repository.create_password_reset_token(user.id, string_context)

        # Prepare reset URL
        reset_url = f"{settings.FRONTEND_HOST}/reset-password?token={reset_token.token_hash}&email={user.email}"

        # Prepare email content and send
        data = {
            "app_name": settings.APP_NAME,
            "name": user.name,
            "activate_url": reset_url,
        }
        subject = f"Reset Password - {settings.APP_NAME}"

        await send_email(
            recipients=[user.email],
            subject=subject,
            template_name="users/password-reset.html",
            context=data,
            bg_task=background_tasks
        )


    async def reset_password(self, email: str, token: str, new_password: str):
        """Validate password reset token and update user's password."""

        # Fetch user
        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid request")

        # Validate reset token
        reset_token  = self.password_reset_repository.get_valid_reset_token(user.id, token)
        if not reset_token:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        # Update password
        user.password = security.hash_password(new_password)  # Hash it before storing
        self.user_repository.update_user(user)

        # Remove used token
        self.password_reset_repository.delete_reset_token(reset_token)

        return {"message": "Password updated successfully"}
