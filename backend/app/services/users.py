from datetime import datetime, timedelta
import logging

from fastapi import HTTPException,BackgroundTasks

from backend.app.core.security import Security
from backend.app.models.users import User, UserToken
from backend.app.core.config import get_settings
from backend.app.repository.users import UserRepository
from backend.app.responses.users import UserResponse

settings = get_settings()
security = Security()

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user_account(self, data, background_tasks: BackgroundTasks):
        user_exist = self.user_repository.get_user_by_email(data.email)
        if user_exist:
            raise HTTPException(status_code=400, detail="Email already exists.")
        if not security.is_password_strong_enough(data.password):
            raise HTTPException(status_code=400, detail="Please provide a strong password.")
        user = User(
            name=data.name,
            email=data.email,
            password=security.hash_password(data.password),
            is_active=False,
            updated_at=datetime.now()
        )
        self.user_repository.create_user(user)
        # Return a response model
        user_response = UserResponse(
            id=user.id,  # Assuming the ID is set after user creation
            name=user.name,
            email=user.email
        )

        # TODO: Send email account verification email

        return user_response