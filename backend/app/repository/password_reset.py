from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import hashlib
from backend.app.models.users import PasswordResetToken


class PasswordResetRepository:
    @staticmethod
    def create_password_reset_token(user_id: int, string_context: str, session: Session) -> PasswordResetToken:
        """Create and store a password reset token in the database."""

        # Hash the context string using SHA-256
        token_hash = hashlib.sha256(string_context.encode("utf-8")).hexdigest()

        # Set expiration time for the token (e.g., 1 hour from now)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        # Create token entry
        reset_token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        # Store token in DB
        session.add(reset_token)
        session.commit()
        session.refresh(reset_token)

        return reset_token

    @staticmethod
    def get_valid_reset_token(user_id: int, token: str, session: Session) -> PasswordResetToken | None:
        """Retrieve a valid reset token if it exists and is not expired."""

        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        return (
            session.query(PasswordResetToken)
            .filter(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.expires_at > datetime.now(timezone.utc),
            )
            .first()
        )

    @staticmethod
    def delete_reset_token(reset_token: PasswordResetToken, session: Session):
        """Delete a password reset token after it's been used."""
        session.delete(reset_token)
        session.commit()
