from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import hashlib
from backend.app.models.users import PasswordResetToken


class PasswordResetRepository:
    def __init__(self, session: Session):  # Fixed typo
        self.session = session

    def create_password_reset_token(self, user_id: int, string_context: str) -> PasswordResetToken:
        """Create and store a password reset token in the database."""
        token_hash = hashlib.sha256(string_context.encode("utf-8")).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        reset_token = PasswordResetToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        self.session.add(reset_token)
        self.session.commit()
        self.session.refresh(reset_token)

        return reset_token

    def get_valid_reset_token(self, user_id: int, token: str) -> PasswordResetToken | None:
        """Retrieve a valid reset token if it exists and is not expired."""
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        return (
            self.session.query(PasswordResetToken)
            .filter(
                PasswordResetToken.user_id == user_id,
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.expires_at > datetime.now(timezone.utc),
            )
            .first()
        )

    def delete_reset_token(self, reset_token: PasswordResetToken):
        """Delete a password reset token after it's been used."""
        self.session.delete(reset_token)
        self.session.commit()
