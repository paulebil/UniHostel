from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from backend.app.repository.password_reset import PasswordResetRepository
from backend.app.services.email_service import send_email
from backend.app.models.users import User
from backend.app.core.config import get_settings

settings = get_settings()


class PasswordResetService:
    @staticmethod
    async def send_password_reset_email(user: User, background_tasks: BackgroundTasks, session: Session):
        """Generate password reset token and send email to the user."""

        string_context = user.get_context_string(context="FORGOT_PASSWORD")

        # Store token in the database
        reset_token = PasswordResetRepository.create_password_reset_token(user.id, string_context, session)

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

    @staticmethod
    async def reset_password(email: str, token: str, new_password: str, session: Session):
        """Validate password reset token and update user's password."""

        # Fetch user
        user = session.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid request")

        # Validate reset token
        reset_token = PasswordResetRepository.get_valid_reset_token(user.id, token, session)
        if not reset_token:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        # Update password
        user.password = new_password  # Hash it before storing
        session.commit()

        # Remove used token
        PasswordResetRepository.delete_reset_token(reset_token, session)

        return {"message": "Password updated successfully"}
