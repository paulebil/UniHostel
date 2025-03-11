from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException

from sqlalchemy.orm import Session

from backend.app.schemas.users import UserCreateSchema
from backend.app.services.users import UserService
from backend.app.repository.users import UserRepository
from backend.app.database.database import get_session

user_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}}
)

def get_user_service(session: Session = Depends(get_session)) -> UserService:
    user_repository = UserRepository(session)
    return UserService(user_repository)

@user_router.post("/create", response_model=UserCreateSchema)
async def create_user(data: UserCreateSchema, background_task: BackgroundTasks, user_service: UserService = Depends(get_user_service)):
    return await user_service.create_user_account(data, background_task)

