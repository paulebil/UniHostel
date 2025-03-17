from datetime import datetime, timedelta
import logging

from fastapi import HTTPException,BackgroundTasks

from sqlalchemy.orm import Session, joinedload

from backend.app.core.security import Security
from backend.app.models.users import User, UserToken
from backend.app.core.config import get_settings
from backend.app.repository.users import UserRepository
from backend.app.responses.users import UserResponse
from backend.app.schemas.users import *
from backend.app.services.email_service import UserAuthEmailService
from backend.app.utils.email_context import USER_VERIFY_ACCOUNT, FORGOT_PASSWORD

settings = get_settings()
security = Security()


class UserService:
    """
     UserService is a stateful service class that manages user-related operations.

     Why is this class stateful?
     - It relies on dependency injection (UserRepository) to interact with the database.
     - Keeping it stateful allows for easier testing and flexibility (e.g., swapping repositories).
     - It follows best practices in backend development, making the code more scalable and maintainable.

     Alternative Approach:
     - Making this class stateless (using @staticmethod) would tightly couple it to UserRepository,
       making it harder to replace or mock dependencies for testing.
     """
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user_account(self, data: UserCreateSchema, background_tasks: BackgroundTasks):
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
        await UserAuthEmailService.send_account_verification_email(user, background_task=background_tasks)

        return user_response

    async def activate_user_account(self, data: ActivateUserSchema, background_tasks: BackgroundTasks):
        user = self.user_repository.get_user_by_email(data.email)
        if not user:
            raise HTTPException(status_code=400, detail="This link is not valid")
        user_token = user.get_context_string(context=USER_VERIFY_ACCOUNT)
        try:
            token_valid = Security.verify_password(user_token, data.token)
        except Exception as verify_exec:
            logging.exception(verify_exec)
            token_valid = False

        if not token_valid:
            raise HTTPException(status_code=400, detail="This link is either expired or not valid.")

        # update the fields
        user.is_active = True
        user.verified_at = datetime.now()
        user.updated_at = datetime.now()
        self.user_repository.update_user(user)

        # Send activation confirmation email
        await UserAuthEmailService.send_account_activation_confirmation_email(user, background_task=background_tasks)

    @staticmethod
    async def get_login_token(data: UserLoginSchema, session: Session):
        user = await security.load_user(data.username, session=session)

        if not user:
            raise HTTPException(status_code=400, detail="Email not registered with us.")
        if not Security.verify_password(data.password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect email or password.")
        if not user.verified_at:
            raise HTTPException(status_code=400, detail="Your account has been deactivated. Please check your email inbox to verify your account.")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Your account has been deactivated. Please contact support.")

        # TODO: Generate the jwt token and return it

        return security.generate_token_pair(user, session)

    @staticmethod
    async def get_refresh_token(self, refresh_token, session: Session):
        token_payload = security.get_token_payload(refresh_token)
        if not token_payload:
            raise HTTPException(status_code=400, detail="Invalid Request.")
        refresh_key = token_payload.get('t')
        access_key = token_payload.get('a')

        user_id = security.str_decode(token_payload.get('sub'))
        user_token = session.query(UserToken).options(joinedload(UserToken.user)).filter(UserToken.refresh_key == refresh_key,
                                                                                         UserToken.access_key == access_key,
                                                                                         UserToken.user_id == user_id,
                                                                                         UserToken.expires_at > datetime.now()
                                                                                         ).first()

        if not user_token:
            raise HTTPException(status_code=400, detail="Invalid Request.")

        user_token.expires_at = datetime.now()
        session.add(user_token)
        session.commit()

        return security.generate_token_pair(UserToken.user, session=session)

    @staticmethod
    async def email_forgot_password_link(self, data: UserForgotPasswordSchema, background_tasks: BackgroundTasks, session: Session):
        user = await security.load_user(data.email, session)
        if not user.verified_at:
            raise HTTPException(status_code=400, detail="Your account is not verified. Please check your email inbox to verify your account.")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Your account has been deactivated. Please contact support.")

        await UserAuthEmailService.send_password_reset_email(user, background_tasks)


    async def reset_password(self, data: UserRestPasswordSchema, session: Session):
        user = await security.load_user(data.email, session)

        if not user:
            raise HTTPException(status_code=400, detail="Invalid request")
        if not user.verified_at:
            raise HTTPException(status_code=400, detail="Invalid request")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Invalid request")

        user_token = user.get_context_string(context=FORGOT_PASSWORD)

        try:
            token_valid = security.verify_password(user_token, data.token)
        except Exception as verify_exec:
            logging.exception(verify_exec)
            token_valid = False
        if not token_valid:
            raise HTTPException(status_code=400, detail="Invalid request window.")

        user.password = security.hash_password(data.password)
        user.updated_at = datetime.now()

        self.user_repository.update_user(user)

        # TODO: Notify user that password has been updated

    async def fetch_user_detail(self, user_id):
        user = self.user_repository.get_user_by_id(user_id)
        if user:
            return user
        raise HTTPException(status_code=400, detail="User does not exists.")