from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from backend.app.models.users import User, UserToken
from sqlalchemy.exc import IntegrityError

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_email(self, email: str) -> User:
        stmt = select(User).where(User.email == email)
        return self.session.execute(stmt).scalars().first()

    def create_user(self, user: User) -> None:
        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
        except IntegrityError:
            self.session.rollback()
            raise

    def update_user(self, user: User) -> None:
        try:
            # updated_at is now handled by the database via onupdate=func.now()
            self.session.commit()
            self.session.refresh(user)
        except IntegrityError:
            self.session.rollback()
            raise

    def get_user_by_id(self, user_id: int) -> User:
        stmt = select(User).where(User.id == user_id)
        return self.session.execute(stmt).scalars().first()

    def add_user_token(self, user_token: UserToken) -> None:
        try:
            self.session.add(user_token)
            self.session.commit()
            self.session.refresh(user_token)
        except IntegrityError:
            self.session.rollback()
            raise

    def get_user_token(self, refresh_key: str, access_key: str, user_id: int) -> UserToken:
        stmt = (
            select(UserToken)
            .options(joinedload(UserToken.user))
            .where(
                UserToken.refresh_key == refresh_key,
                UserToken.access_key == access_key,
                UserToken.user_id == user_id,
                UserToken.expires_at > datetime.now(timezone.utc)
            )
        )
        return self.session.execute(stmt).scalars().first()

    def update_user_token(self, user_token: UserToken) -> None:
        try:
            user_token.expires_at = datetime.now(timezone.utc)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise