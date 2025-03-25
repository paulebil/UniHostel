from fastapi import APIRouter, Depends, status, HTTPException

from backend.app.schemas.hostels import HostelCreateSchema
from backend.app.responses.hostels import HostelListResponse, HostelResponse
from backend.app.services.hostels import HostelService
from backend.app.repository.hostels import HostelRepository
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


def get_hostel_service(session: Session = Depends(get_session)) -> HostelService:
    hostel_repository = HostelRepository(session)
    return HostelService(hostel_repository)

@hostel_router.post("/create", status_code=status.HTTP_201_CREATED, response_model=HostelResponse)
async def create_hostel(data: HostelCreateSchema, hostel_service: HostelService = Depends(get_hostel_service),
                        current_user = Depends(security.get_current_user)):
    return await hostel_service.create_hostel(data, current_user)



