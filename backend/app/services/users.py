from datetime import datetime
import logging
from fastapi import HTTPException, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session, joinedload
from starlette.responses import JSONResponse

from backend.app.core.security import Security
from backend.app.models.users import User, UserToken
from backend.app.core.config import get_settings
from backend.app.repository.users import UserRepository
from backend.app.responses.users import UserResponse, AllUserResponse
from backend.app.responses.students import StudentBase
from backend.app.responses.custodian import HostelOwnerBase
from backend.app.schemas.users import *
from backend.app.services.email_service import UserAuthEmailService
from backend.app.services.password_reset import PasswordResetService
from backend.app.repository.password_reset import PasswordResetRepository
from backend.app.utils.email_context import USER_VERIFY_ACCOUNT
from backend.app.database.database import get_session

settings = get_settings()
security = Security()
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_repository: UserRepository,password_reset_repository: PasswordResetRepository):
        self.user_repository = user_repository
        self.password_reset_service = PasswordResetService(password_reset_repository, user_repository)

    async def create_user_account(self, data: UserCreateSchema, background_tasks: BackgroundTasks):
        user_exist = self.user_repository.get_user_by_email(data.email)
        if user_exist:
            raise HTTPException(status_code=400, detail="Email already exists.")
        user_number_exists = self.user_repository.get_user_by_mobile(data.mobile)
        if user_number_exists:
            raise HTTPException(status_code=400, detail="Mobile number already exists.")
        if not security.is_password_strong_enough(data.password):
            raise HTTPException(status_code=400, detail="Please provide a strong password.")

        user = User(
            name=data.name,
            email=data.email,
            role=data.role,
            mobile=data.mobile,
            password=security.hash_password(data.password),
            is_active=False,
            updated_at=datetime.now()
        )
        self.user_repository.create_user(user)
        user_response = UserResponse(id=user.id, name=user.name, email=user.email, mobile=user.mobile)
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
        user.is_active = True
        user.verified_at = datetime.now()
        user.updated_at = datetime.now()
        self.user_repository.update_user(user)
        await UserAuthEmailService.send_account_activation_confirmation_email(user, background_task=background_tasks)

    @staticmethod
    async def get_login_token(data: UserLoginSchema, session: Session = Depends(get_session)):
        user = await security.load_user(data.username, session=session)
        if not user:
            raise HTTPException(status_code=400, detail="Email not registered with us.")
        if not Security.verify_password(data.password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect email or password.")
        if not user.verified_at:
            raise HTTPException(status_code=400, detail="Your account has not been verified.")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Your account has been deactivated.")
        return security.generate_token_pair(user, session)

    @staticmethod
    async def get_refresh_token(refresh_token: str, session: Session = Depends(get_session)):
        logger.info("Received refresh token request.")
        token_payload = security.get_token_payload(refresh_token)
        if not token_payload:
            raise HTTPException(status_code=400, detail="Invalid Request.")
        refresh_key = token_payload.get('t')
        access_key = token_payload.get('a')
        user_id = security.str_decode(token_payload.get('sub'))
        user_token = (
            session.query(UserToken)
            .options(joinedload(UserToken.user))
            .filter(
                UserToken.refresh_key == refresh_key,
                UserToken.access_key == access_key,
                UserToken.user_id == user_id,
                UserToken.expires_at > datetime.now(),
            )
            .first()
        )
        if not user_token or not user_token.user:
            raise HTTPException(status_code=400, detail="Invalid Request.")
        user_token.expires_at = datetime.now()
        session.add(user_token)
        session.commit()
        return security.generate_token_pair(user_token.user, session=session)

    async def email_forgot_password_link(self, data: UserForgotPasswordSchema, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
        user = await security.load_user(data.email, session)
        if not user.verified_at:
            raise HTTPException(status_code=400, detail="Your account is not verified.")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Your account has been deactivated.")
        await self.password_reset_service.send_password_reset_email(user, background_tasks)

    async def reset_password(self, data: UserRestPasswordSchema, session: Session = Depends(get_session)):
        logger.info(f"Received password reset request for email: {data.email}")
        user = await security.load_user(data.email, session)
        if not user or not user.verified_at or not user.is_active:
            raise HTTPException(status_code=400, detail="Invalid request")
        token_valid = self.password_reset_service.reset_password(user.email, data.token, data.password)
        if not token_valid:
            raise HTTPException(status_code=400, detail="Invalid request window.")
        user.password = security.hash_password(data.password)
        user.updated_at = datetime.now()
        self.user_repository.update_user(user)
        return JSONResponse({"message": "Password updated successfully"})

    async def fetch_user_detail(self, user_id):
        user = self.user_repository.get_user_by_id(user_id)
        user =  AllUserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            mobile=user.mobile,
            role=user.role.value,
            is_active=user.is_active,
            verified_at=user.verified_at,
            updated_at=user.updated_at,
            student=StudentBase(
                student_number=user.student.student_number,
                university_name=user.student.university_name
            ) if user.student else None,
            hostel_owner=[HostelOwnerBase(
                business_name=user.hostel_owner.business_name,
            ) ]if user.hostel_owner else None,
        )
        if user:
            return user
        raise HTTPException(status_code=400, detail="User does not exist.")

    async def fetch_all_users(self, current_user: User):
        if not current_user.role == UserRole.ADMIN.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not an admin to access this route")
        users = self.user_repository.get_all_users()
        return [
            AllUserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                mobile=user.mobile,
                role=user.role.value,
                is_active=user.is_active,
                verified_at=user.verified_at,
                updated_at=user.updated_at,
                student=StudentBase(
                    student_number=user.student.student_number,
                    university_name=user.student.university_name
                ) if user.student else None,
                hostel_owner=[
                    HostelOwnerBase(business_name=owner.business_name)
                    for owner in user.hostel_owner
                ] if user.hostel_owner else []
            ) for user in users
        ]
