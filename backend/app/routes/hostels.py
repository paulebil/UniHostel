from fastapi import APIRouter, Depends, status

from backend.app.schemas.hostels import *
from backend.app.responses.hostels import HostelListResponse, HostelResponse
from backend.app.services.hostels import HostelService
from backend.app.repository.hostels import HostelRepository
from backend.app.repository.custodian import HostelOwnerRepository
from backend.app.database.database import get_session
from backend.app.core.security import Security


from sqlalchemy.orm import Session

security = Security()

hostel_router = APIRouter(
    prefix="/hostels",
    tags=["Hostels"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(security.get_current_user)]
)

hostel_user_router = APIRouter(
    prefix="/hostels",
    tags=["Hostels"],
    responses={404: {"description": "Not found"}},
)


def get_hostel_service(session: Session = Depends(get_session)) -> HostelService:
    hostel_repository = HostelRepository(session)
    hostel_owner_repository = HostelOwnerRepository(session)
    return HostelService(hostel_repository, hostel_owner_repository)

@hostel_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=HostelResponse)
async def create_hostel(data: HostelCreateSchema, hostel_service: HostelService = Depends(get_hostel_service),
                        current_user = Depends(security.get_current_user)):
    return await hostel_service.create_hostel(data, current_user)

@hostel_router.put("/update", status_code=status.HTTP_200_OK , response_model=HostelResponse)
async def update_hostel(data: HostelUpdateSchema, hostel_service: HostelService = Depends(get_hostel_service),
                        current_user = Depends(security.get_current_user)):
    return await hostel_service.update_hostel(data, current_user)

@hostel_router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_hostel(hostel_id: int, hostel_service: HostelService = Depends(get_hostel_service),
                        current_user = Depends(security.get_current_user)):
    return await hostel_service.delete_hostel(hostel_id, current_user)

@hostel_user_router.get("/all-hostels", status_code=status.HTTP_200_OK, response_model=HostelListResponse)
async def get_all_hostels(hostel_service: HostelService = Depends(get_hostel_service)):
    return await hostel_service.get_all_hostels()

