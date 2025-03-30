from fastapi import APIRouter, Depends, BackgroundTasks,status, Header
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from backend.app.database.database import get_session

from backend.app.services.users import UserService, security
from backend.app.repository.users import UserRepository
from backend.app.repository.password_reset import PasswordResetRepository
from backend.app.responses.users import *
from backend.app.schemas.users import *

from backend.app.repository.student import StudentRepository
from backend.app.services.student import StudentService
from backend.app.responses.students import *
from backend.app.schemas.students import *

from backend.app.repository.custodian import HostelOwnerRepository
from backend.app.services.custodain import HostelOwnerService
from backend.app.responses.custodian import *
from backend.app.schemas.custodian import *




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
    dependencies=[Depends(security.oauth2_scheme), Depends(security.get_current_user)]
)

admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(security.oauth2_scheme), Depends(security.get_current_user)]
)

def get_user_service(session: Session = Depends(get_session)) -> UserService:
    user_repository = UserRepository(session)
    password_reset_repository = PasswordResetRepository(session)
    return UserService(user_repository, password_reset_repository)

def get_student_service(session: Session = Depends(get_session)) -> StudentService:
    user_repository = UserRepository(session)
    student_repository = StudentRepository(session)
    return StudentService(student_repository, user_repository)

def get_hostel_owner_service(session: Session = Depends(get_session)) -> HostelOwnerService:
    user_repository = UserRepository(session)
    hostel_owner_repo = HostelOwnerRepository(session)
    return HostelOwnerService(hostel_owner_repo, user_repository)

@user_router.post("/create", status_code=status.HTTP_201_CREATED,response_model=UserResponse)
async def create_user(data: UserCreateSchema, background_task: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user_account(data, background_task)

@user_router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_user(data: ActivateUserSchema, background_tasks: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    await  user_service.activate_user_account(data, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})

@guest_router.post("/login", status_code=status.HTTP_200_OK, response_model=UserLoginResponse)
async def user_login(data: OAuth2PasswordRequestForm = Depends(), user_service: UserService = Depends(get_user_service), session: Session = Depends(get_session)):
    user = await user_service.get_login_token(data, session)
    return user

@guest_router.post("/refresh", status_code=status.HTTP_200_OK, response_model=UserLoginResponse)
async def refresh_token(refresh_token = Header(), user_service: UserService = Depends(get_user_service), session: Session = Depends(get_session)):
    return await user_service.get_refresh_token(refresh_token, session)

@guest_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data: UserForgotPasswordSchema, background_tasks: BackgroundTasks, session: Session = Depends(get_session), user_service: UserService = Depends(get_user_service)):
    await user_service.email_forgot_password_link(data, background_tasks, session)
    return JSONResponse({"message": "A email with password reset link has been sent to you."})

@guest_router.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(data: UserRestPasswordSchema, session: Session = Depends(get_session), user_service: UserService = Depends(get_user_service)):
    await user_service.reset_password(data, session)
    return JSONResponse({"message": "Your password has been updated."})

@auth_router.get("/me", status_code=status.HTTP_200_OK, response_model=AllUserResponse)
async def fetch_user(user=Depends(security.get_current_user), token: str = Header(None), user_service: UserService = Depends(get_user_service)):  # Use Header instead
    user_obj = await user_service.fetch_user_detail(user.id)
    return user_obj

@auth_router.post("/create-student", status_code=status.HTTP_201_CREATED, response_model=StudentResponse)
async def create_student(data: StudentCreate, student_service: StudentService = Depends(get_student_service)):
    return await student_service.create_student(data)

@auth_router.put("/update-student", status_code=status.HTTP_200_OK, response_model=StudentResponse)
async def update_student(data: StudentUpdate, student_service: StudentService = Depends(get_student_service)):
    return await student_service.update_student(data)

@auth_router.delete("/delete-student", status_code=status.HTTP_200_OK)
async def delete_student(email: str, student_service: StudentService = Depends(get_student_service)):
    return await student_service.delete_student(email)

@auth_router.get("/get-student", status_code=status.HTTP_200_OK, response_model=StudentResponse)
async def get_student(email: str, student_service: StudentService = Depends(get_student_service)):
    return await student_service.get_student_information(email)

@auth_router.post("/create-owner", status_code=status.HTTP_201_CREATED, response_model=HostelOwnerResponse)
async def create_owner(data: HostelOwnerCreate,
                       hostel_owner_service: HostelOwnerService = Depends(get_hostel_owner_service)):
    return await hostel_owner_service.create_hostel_owner(data)

@auth_router.put("/update-owner", status_code=status.HTTP_200_OK, response_model=HostelOwnerResponse)
async def update_owner(data: HostelOwnerUpdate,
                       hostel_owner_service: HostelOwnerService = Depends(get_hostel_owner_service)):
    return await hostel_owner_service.update_hostel_owner(data)

@auth_router.delete("/delete-owner", status_code=status.HTTP_200_OK)
async def delete_owner(email: str, hostel_owner_service: HostelOwnerService = Depends(get_hostel_owner_service)):
    return await hostel_owner_service.delete_hostel_owner(email)

@auth_router.get("/get-owner", status_code=status.HTTP_200_OK, response_model=HostelOwnerResponse)
async def get_owner(email: str, hostel_owner_service: HostelOwnerService = Depends(get_hostel_owner_service)):
    return await hostel_owner_service.get_hostel_owner_information(email)

@admin_router.get("/users", response_model=list[AllUserResponse])
async def get_all_users(user_service: UserService = Depends(get_user_service), current_user = Depends(security.get_current_user)):
    return await user_service.fetch_all_users(current_user)