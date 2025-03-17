from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status, Header
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from backend.app.schemas.users import *
from backend.app.services.users import UserService
from backend.app.repository.users import UserRepository
from backend.app.database.database import get_session
from backend.app.responses.users import *
from backend.app.core.security import Security

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)

guest_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

auth_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(Security.oauth2_scheme), Depends(Security.get_current_user)]
)

def get_user_service(session: Session = Depends(get_session)) -> UserService:
    user_repository = UserRepository(session)
    return UserService(user_repository)

@user_router.post("/create", status_code=status.HTTP_201_CREATED,response_model=UserResponse)
async def create_user(data: CreateUser, background_task: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user_account(data, background_task)

@user_router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user(data: ActivateUser, background_tasks: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    await  user_service.activate_user_account(data, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})

@guest_router.post("/login", status_code=status.HTTP_200_OK, response_model=UserLoginResponse)
async def user_login(data: OAuth2PasswordRequestForm = Depends(), user_service: UserService = Depends(get_user_service), session: Session = Depends(get_session)):
    return await user_service.get_login_token(data, session=session)

@guest_router.post("/refresh", status_code=status.HTTP_200_OK, response_model=UserLoginResponse)
async def refresh_token(refresh_token = Header(), user_service: UserService = Depends(get_user_service), session: Session = Depends(get_session)):
    return await user_service.get_refresh_token(refresh_token, session)

@guest_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data: ForgotPassword, background_tasks: BackgroundTasks, session: Session = Depends(get_session), user_service: UserService = Depends(get_user_service)):
    await user_service.email_forgot_password_link(data, background_tasks, session)
    return JSONResponse({"message": "A email with password reset link has been sent to you."})

@guest_router.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(data: RestPassword, session: Session = Depends(get_session), user_service: UserService = Depends(get_user_service)):
    await user_service.reset_password(data, session)
    return JSONResponse({"message": "Your password has been updated."})

@auth_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def fetch_user(user = Depends(Security.get_current_user)):
    return user
