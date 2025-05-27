from fastapi import APIRouter, Depends, status, Form, File, UploadFile

from backend.app.schemas.hostels import *
from backend.app.responses.hostels import *
from backend.app.services.hostels import HostelService
from backend.app.repository.hostels import HostelRepository
from backend.app.repository.images import ImageMetaDataRepository
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
    tags=["Students"],
    responses={404: {"description": "Not found"}},
)


def get_hostel_service(session: Session = Depends(get_session)) -> HostelService:
    hostel_repository = HostelRepository(session)
    image_repository = ImageMetaDataRepository(session)
    return HostelService(hostel_repository, image_repository)

@hostel_router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_hostel(name: str = Form(), location: str = Form(...),average_price:int = Form(),
                      available_rooms: int = Form(), description: str = Form(...), rules_and_regulations: str = Form(),
                      amenities: str = Form(),images: List[UploadFile] = File(...),
                      hostel_service: HostelService = Depends(get_hostel_service),
                      current_user = Depends(security.get_current_user)):

    data = HostelCreateSchema(
        name=name,
        description=description,
        location=location,
        average_price=average_price,
        available_rooms=available_rooms,
        amenities=amenities,
        rules_and_regulations=rules_and_regulations
    )

    return await hostel_service.create_hostel(images, data, current_user)

@hostel_router.put("/update", status_code=status.HTTP_200_OK , response_model=HostelResponse)
async def update_hostel(data: HostelUpdateSchema, hostel_service: HostelService = Depends(get_hostel_service),
                        current_user = Depends(security.get_current_user)):
    return await hostel_service.update_hostel(data, current_user)

@hostel_router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_hostel(hostel_id: int, hostel_service: HostelService = Depends(get_hostel_service),
                        current_user = Depends(security.get_current_user)):
    return await hostel_service.delete_hostel(hostel_id, current_user)

@hostel_router.get("/my-hostels", status_code=status.HTTP_200_OK, response_model=HostelListResponse)
async def get_all_my_hostels(hostel_service: HostelService = Depends(get_hostel_service),
                             current_user = Depends(security.get_current_user)):
    return await hostel_service.get_all_my_hostels(current_user)

@hostel_router.get("/hostel-detail", status_code=status.HTTP_200_OK, response_model=HostelResponse)
async def get_hostel_detail(hostel_id: int, hostel_service: HostelService = Depends(get_hostel_service),
                            current_user =Depends(security.get_current_user)):
    return await hostel_service.get_hostel_detail(hostel_id, current_user)

################### Student endpoints

@hostel_user_router.get("/all-hostels", status_code=status.HTTP_200_OK, response_model=HostelListResponse)
async def get_all_hostels(hostel_service: HostelService = Depends(get_hostel_service)):
    return await hostel_service.get_all_hostels()

@hostel_user_router.put("/search", status_code=status.HTTP_200_OK, response_model=HostelListResponse)
async def search_hostels(query:HostelSearchSchema, hostel_service: HostelService = Depends(get_hostel_service)):
    return await hostel_service.search_hostels(query)

@hostel_user_router.get("/hostel-detail-student", status_code=status.HTTP_200_OK, response_model=HostelResponse)
async def get_hostel_detail_student(hostel_id: int, hostel_service: HostelService = Depends(get_hostel_service)):
    return await hostel_service.get_hostel_detail_user(hostel_id)

